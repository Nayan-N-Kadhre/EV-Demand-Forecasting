from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model.train import run as train_run
from src.model.evaluate import run as evaluate_run

default_args = {
    "owner": "nknay",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="retrain_dag",
    default_args=default_args,
    description="Weekly retraining and evaluation of Prophet demand forecasting models",
    schedule="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["model", "retrain", "prophet"],
) as dag:

    train_task = PythonOperator(
        task_id="train_models",
        python_callable=train_run,
    )

    evaluate_task = PythonOperator(
        task_id="evaluate_models",
        python_callable=evaluate_run,
    )

    train_task >> evaluate_task
