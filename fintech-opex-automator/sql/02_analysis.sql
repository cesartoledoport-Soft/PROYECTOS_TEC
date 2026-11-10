-- Costo asignado y variación mensual por área y servicio.
WITH costs AS (
  SELECT d.month_start, a.area_name, s.service_name, SUM(f.allocated_cost_usd) AS allocated_cost_usd
  FROM fact_allocated_cost f JOIN dim_date d ON f.date_key=d.date_key JOIN dim_area a ON f.area_key=a.area_key JOIN dim_service s ON f.service_key=s.service_key
  GROUP BY 1,2,3
)
SELECT *, allocated_cost_usd - LAG(allocated_cost_usd) OVER (PARTITION BY area_name, service_name ORDER BY month_start) AS monthly_variance_usd
FROM costs ORDER BY month_start, allocated_cost_usd DESC;

-- Cola de revisión de gastos anómalos.
SELECT d.month_start, s.service_name, a.area_name, f.allocated_cost_usd, f.anomaly_score
FROM fact_allocated_cost f JOIN dim_date d ON f.date_key=d.date_key JOIN dim_service s ON f.service_key=s.service_key JOIN dim_area a ON f.area_key=a.area_key
WHERE f.anomaly_flag = TRUE ORDER BY ABS(f.anomaly_score) DESC;
