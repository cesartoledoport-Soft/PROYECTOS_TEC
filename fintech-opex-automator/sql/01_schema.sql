-- PostgreSQL: modelo estrella para la salida del pipeline.
CREATE TABLE dim_area (area_key SERIAL PRIMARY KEY, area_code VARCHAR(30) UNIQUE NOT NULL, area_name VARCHAR(100) NOT NULL);
CREATE TABLE dim_service (service_key SERIAL PRIMARY KEY, service_name VARCHAR(100) UNIQUE NOT NULL, expense_type VARCHAR(50) NOT NULL);
CREATE TABLE dim_date (date_key INTEGER PRIMARY KEY, calendar_date DATE UNIQUE NOT NULL, month_start DATE NOT NULL, year_num SMALLINT NOT NULL, month_num SMALLINT NOT NULL);
CREATE TABLE fact_allocated_cost (
  allocation_id VARCHAR(50) PRIMARY KEY, expense_id VARCHAR(50) NOT NULL, date_key INTEGER REFERENCES dim_date(date_key),
  service_key INTEGER REFERENCES dim_service(service_key), area_key INTEGER REFERENCES dim_area(area_key), vendor VARCHAR(120) NOT NULL,
  allocation_method VARCHAR(20) NOT NULL CHECK (allocation_method IN ('DIRECT','USAGE')),
  usage_units NUMERIC(18,2), source_amount_usd NUMERIC(18,2) NOT NULL, allocated_cost_usd NUMERIC(18,2) NOT NULL,
  anomaly_flag BOOLEAN NOT NULL DEFAULT FALSE, anomaly_score NUMERIC(12,4)
);
CREATE INDEX ix_cost_month_service ON fact_allocated_cost(date_key, service_key);
