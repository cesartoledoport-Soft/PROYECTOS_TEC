import pandas as pd
import pytest
from src.pipeline import allocate_costs, clean_expenses


def test_shared_expense_is_allocated_by_usage_and_conserves_cost():
    expenses = clean_expenses(pd.DataFrame([{"expense_id":"E1","invoice_date":"2026-01-01","vendor":"AWS","service":"Compute","expense_type":"Infrastructure","cost_center":"SHARED","amount":100,"currency":"USD","fx_to_usd":1}]))
    usage = pd.DataFrame([{"month":"2026-01","service":"Compute","area":"ENG","usage_units":75,"usage_metric":"hours"},{"month":"2026-01","service":"Compute","area":"DATA","usage_units":25,"usage_metric":"hours"}])
    result = allocate_costs(expenses, usage)
    assert result["allocated_cost_usd"].sum() == 100
    assert result.set_index("area").loc["ENG", "allocated_cost_usd"] == 75


def test_shared_expense_without_driver_fails():
    expenses = clean_expenses(pd.DataFrame([{"expense_id":"E1","invoice_date":"2026-01-01","vendor":"AWS","service":"Compute","expense_type":"Infrastructure","cost_center":"SHARED","amount":100,"currency":"USD","fx_to_usd":1}]))
    with pytest.raises(ValueError, match="No existe driver"):
        allocate_costs(expenses, pd.DataFrame(columns=["month","service","area","usage_units","usage_metric"]))
