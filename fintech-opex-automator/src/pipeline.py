"""Clean, allocate and monitor technology operating expenses."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

VENDOR_MAP = {"amazon aws": "AWS", "amazon web services": "AWS", "aws": "AWS"}
REQUIRED_EXPENSE_COLUMNS = {"expense_id", "invoice_date", "vendor", "service", "expense_type", "cost_center", "amount", "currency", "fx_to_usd"}
REQUIRED_USAGE_COLUMNS = {"month", "service", "area", "usage_units", "usage_metric"}


def validate_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{label}: faltan columnas obligatorias: {', '.join(sorted(missing))}")


def clean_expenses(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize source records and reject inputs that cannot be allocated safely."""
    validate_columns(frame, REQUIRED_EXPENSE_COLUMNS, "expenses")
    data = frame.copy()
    data["invoice_date"] = pd.to_datetime(data["invoice_date"], errors="coerce")
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
    data["fx_to_usd"] = pd.to_numeric(data["fx_to_usd"], errors="coerce")
    if data["expense_id"].duplicated().any():
        raise ValueError("expenses: existen expense_id duplicados")
    if data[["invoice_date", "amount", "fx_to_usd"]].isna().any().any() or (data["amount"] < 0).any() or (data["fx_to_usd"] <= 0).any():
        raise ValueError("expenses: fecha, importe o tipo de cambio inválido")
    data["vendor"] = data["vendor"].str.strip().str.lower().map(VENDOR_MAP).fillna(data["vendor"].str.strip())
    data["service"] = data["service"].str.strip().str.title()
    data["cost_center"] = data["cost_center"].str.strip().str.upper()
    data["month"] = data["invoice_date"].dt.to_period("M").astype(str)
    data["amount_usd"] = (data["amount"] * data["fx_to_usd"]).round(2)
    return data


def allocate_costs(expenses: pd.DataFrame, usage: pd.DataFrame) -> pd.DataFrame:
    """Allocate direct expenses to their center and shared expenses by monthly usage."""
    validate_columns(usage, REQUIRED_USAGE_COLUMNS, "usage")
    usage = usage.copy()
    usage["month"] = usage["month"].astype(str)
    usage["service"] = usage["service"].str.strip().str.title()
    usage["area"] = usage["area"].str.strip().str.upper()
    usage["usage_units"] = pd.to_numeric(usage["usage_units"], errors="coerce")
    if usage["usage_units"].isna().any() or (usage["usage_units"] < 0).any():
        raise ValueError("usage: unidades inválidas")
    rows: list[dict] = []
    for expense in expenses.to_dict("records"):
        if expense["cost_center"] != "SHARED":
            rows.append({**expense, "area": expense["cost_center"], "allocation_method": "DIRECT", "usage_units": None, "allocation_share": 1.0, "allocated_cost_usd": expense["amount_usd"]})
            continue
        drivers = usage[(usage["month"] == expense["month"]) & (usage["service"] == expense["service"])]
        total_usage = drivers["usage_units"].sum()
        if drivers.empty or total_usage <= 0:
            raise ValueError(f"No existe driver de uso para gasto compartido {expense['expense_id']} ({expense['month']} / {expense['service']})")
        for driver in drivers.to_dict("records"):
            share = driver["usage_units"] / total_usage
            rows.append({**expense, "area": driver["area"], "allocation_method": "USAGE", "usage_units": driver["usage_units"], "allocation_share": share, "allocated_cost_usd": round(expense["amount_usd"] * share, 2)})
    allocated = pd.DataFrame(rows)
    # Rounding differences are assigned to the largest allocation in each source expense.
    for expense_id, group in allocated.groupby("expense_id"):
        difference = round(group["amount_usd"].iloc[0] - group["allocated_cost_usd"].sum(), 2)
        if difference:
            allocated.loc[group["allocated_cost_usd"].idxmax(), "allocated_cost_usd"] += difference
    return allocated


def add_anomaly_flags(allocated: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
    """Flag unusual source expenses using z-score within each service history."""
    data = allocated.copy()
    source = data.drop_duplicates("expense_id").copy()
    stats = source.groupby("service")["amount_usd"].agg(["mean", "std", "count"]).rename(columns={"mean": "service_mean", "std": "service_std", "count": "observations"})
    source = source.join(stats, on="service")
    source["anomaly_score"] = ((source["amount_usd"] - source["service_mean"]) / source["service_std"]).where(source["observations"] >= 3)
    source["anomaly_flag"] = source["anomaly_score"].abs().ge(threshold).fillna(False)
    return data.merge(source[["expense_id", "anomaly_score", "anomaly_flag"]], on="expense_id", how="left")


def run_pipeline(input_path: Path, usage_path: Path, output_dir: Path, threshold: float = 2.0) -> dict:
    expenses = clean_expenses(pd.read_csv(input_path))
    allocated = add_anomaly_flags(allocate_costs(expenses, pd.read_csv(usage_path)), threshold)
    output_dir.mkdir(parents=True, exist_ok=True)
    allocated_columns = ["expense_id", "invoice_date", "month", "vendor", "service", "expense_type", "area", "allocation_method", "usage_units", "amount_usd", "allocated_cost_usd", "anomaly_score", "anomaly_flag"]
    allocated[allocated_columns].sort_values(["month", "expense_id", "area"]).to_csv(output_dir / "fact_allocated_costs.csv", index=False)
    monthly = allocated.groupby(["month", "area", "service"], as_index=False).agg(allocated_cost_usd=("allocated_cost_usd", "sum"), source_expenses=("expense_id", "nunique"))
    monthly.to_csv(output_dir / "monthly_costs.csv", index=False)
    anomalies = allocated[allocated["anomaly_flag"]].sort_values("anomaly_score", key=lambda col: col.abs(), ascending=False)
    anomalies.to_csv(output_dir / "license_anomalies.csv", index=False)
    quality = {"source_expenses": int(len(expenses)), "allocated_rows": int(len(allocated)), "allocated_usd": round(float(allocated["allocated_cost_usd"].sum()), 2), "source_usd": round(float(expenses["amount_usd"].sum()), 2), "anomalous_expenses": int(anomalies["expense_id"].nunique()), "status": "PASS"}
    if quality["allocated_usd"] != quality["source_usd"]:
        raise AssertionError("La asignación no conserva el costo fuente")
    (output_dir / "data_quality_report.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return quality


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatiza asignación de OPEX tecnológico")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--usage", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    parser.add_argument("--threshold", type=float, default=2.0)
    args = parser.parse_args()
    print(json.dumps(run_pipeline(args.input, args.usage, args.output, args.threshold), indent=2))


if __name__ == "__main__":
    main()
