# Guía de reporte Power BI

## Power Query

1. Ejecuta el pipeline: `python -m src.pipeline --input data/raw/expenses.csv --usage data/reference/usage_by_area.csv`.
2. En Power BI Desktop, importa `data/processed/fact_allocated_costs.csv` como **FactAllocatedCosts** y `monthly_costs.csv` como **MonthlyCosts**.
3. Tipos: `invoice_date` como Fecha; todos los campos `*_usd` como Decimal fijo; `anomaly_flag` como Verdadero/Falso.
4. Crea una tabla calendario relacionada con `FactAllocatedCosts[invoice_date]`.

## Medidas DAX

```DAX
Costo asignado USD = SUM(FactAllocatedCosts[allocated_cost_usd])
Costo fuente USD = SUM(FactAllocatedCosts[amount_usd])
Gasto anómalo USD = CALCULATE([Costo asignado USD], FactAllocatedCosts[anomaly_flag] = TRUE())
% gasto anómalo = DIVIDE([Gasto anómalo USD], [Costo asignado USD])
Costo mensual anterior = CALCULATE([Costo asignado USD], DATEADD('Calendar'[Date], -1, MONTH))
Variación mensual USD = [Costo asignado USD] - [Costo mensual anterior]
```

## Diseño propuesto

- **Fila superior:** Costo asignado USD, % gasto anómalo, variación mensual USD y número de servicios.
- **Izquierda:** línea de costo mensual por servicio.
- **Centro:** barras apiladas de costo por área y servicio.
- **Derecha:** tabla de anomalías con mes, servicio, área, monto y `anomaly_score`; filtrar `anomaly_flag = TRUE`.
- Segmentadores: mes, área, proveedor y tipo de gasto.

El archivo `.pbix` no se versiona para mantener el repositorio ligero; este documento permite reconstruir el reporte de forma reproducible.
