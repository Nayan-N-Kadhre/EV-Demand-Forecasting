# EV Charging Station Demand Forecasting Pipeline

## Business problem
EV charging demand is highly variable across stations, hours, and days.
This pipeline forecasts hourly charging demand per station to support
grid load planning, capacity decisions, and operational efficiency.

## Architecture
![Architecture Diagram](docs/architecture.png)

## Tech stack
| Layer | Tool |
|-------|------|
| Orchestration | Apache Airflow 2.9.1 |
| Database | PostgreSQL 15 (Docker) |
| Transform | Python, SQL |
| Modeling | Facebook Prophet |
| Visualization | Tableau Public |
| Version control | Git + GitHub |

## Pipeline structure

raw schema        → ingested from NREL API daily via Airflow
staging schema    → cleaned, validated, type-cast
mart schema       → aggregated hourly, ready for Tableau

## How to run locally
1. Clone the repo
```bash
   git clone https://github.com/Nayan-N-Kadhre/ev-demand-forecasting.git
   cd ev-demand-forecasting
```
2. Start Postgres
```bash
   docker-compose up -d postgres
```
3. Create virtual environment
```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```
4. Run the pipeline
```bash
   airflow dags trigger ingest_dag
```

## Results
_(to be updated after analysis)_

## Key insights
_(to be updated after dashboard is complete)_

## Dashboard
_(Tableau Public link coming soon)_
