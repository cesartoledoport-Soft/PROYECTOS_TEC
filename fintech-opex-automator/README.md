# FinTech Operational Expense Automator

Pipeline reproducible para depurar gastos de infraestructura y distribuirlos entre áreas según consumo. Incluye reglas de calidad, asignación de costos compartidos, detección de anomalías y artefactos listos para Power BI.

## Pregunta de negocio

¿Qué área consume cada servicio TI, cuánto costo directo y compartido absorbe, y qué gastos de licencias requieren revisión?

## Flujo

1. Lee `data/raw/expenses.csv` y `data/reference/usage_by_area.csv`.
2. Normaliza proveedores, fechas, monedas y centros de costo con Pandas.
3. Asigna gastos directos por centro de costo; los compartidos se prorratean por unidades de consumo.
4. Calcula z-score por servicio y marca anomalías sobre el umbral configurable.
5. Escribe `fact_allocated_costs.csv`, `monthly_costs.csv`, `license_anomalies.csv` y `data_quality_report.json` en `data/processed/`.

## Ejecutar

Requiere Python 3.11+.

```bash
python -m venv .venv
.venv\\Scripts\\activate       # Windows PowerShell
pip install -r requirements.txt
python -m src.pipeline --input data/raw/expenses.csv --usage data/reference/usage_by_area.csv
pytest
```

La carpeta de resultados está ignorada porque se genera de forma determinista. Para cargar en Power BI, ejecuta primero el pipeline y sigue [powerbi/REPORT_GUIDE.md](powerbi/REPORT_GUIDE.md).

## Modelo

`sql/01_schema.sql` define un esquema analítico (hecho de costos asignados y dimensiones). `sql/02_analysis.sql` contiene consultas de auditoría que equivalen a las visualizaciones del dashboard.

## Decisiones de ingeniería

- Los importes se conservan en USD; los registros no USD se convierten con la tasa incluida en el archivo fuente.
- Un gasto compartido sin uso asociado se reporta como error de calidad y no se asigna silenciosamente.
- La anomalía se evalúa por servicio contra la distribución histórica disponible; si hay menos de 3 observaciones, se marca como no evaluable.
