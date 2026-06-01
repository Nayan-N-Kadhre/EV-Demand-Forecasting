from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.transform.run_transforms import run as transform_run

default_args = {
    "owner": "nknay",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="transform_dag",
    default_args=default_args,
    description="Daily transformation of raw EV stations into staging and mart layers",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["transform", "ev", "staging", "mart"],
) as dag:

    transform_task = PythonOperator(
        task_id="run_transforms",
        python_callable=transform_run,
    )
