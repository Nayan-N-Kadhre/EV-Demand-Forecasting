from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.extract.fetch_sessions import run as fetch_run
from src.load.load_raw import run as load_run

default_args = {
    "owner": "nknay",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="ingest_dag",
    default_args=default_args,
    description="Daily ingestion of EV station data from NLR API into raw.ev_stations",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ingest", "ev", "raw"],
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_ev_stations",
        python_callable=fetch_run,
    )

    load_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_run,
    )

    fetch_task >> load_task
