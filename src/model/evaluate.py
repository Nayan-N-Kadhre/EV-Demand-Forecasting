import os
import logging
import json
import joblib
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "10.255.255.254")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ev_pipeline")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def load_registry():
    with open("models/model_registry.json", "r") as f:
        return json.load(f)

def generate_test_series(total_ports, seed):
    np.random.seed(seed % 1000)
    dates = pd.date_range(start="2026-01-01", periods=90, freq="D")
    weekday_effect = [1.0, 1.0, 1.0, 1.0, 1.1, 1.3, 1.2]
    values = [
        total_ports * weekday_effect[d.weekday()] + np.random.normal(0, total_ports * 0.05)
        for d in dates
    ]
    return pd.DataFrame({"ds": dates, "y": values})

def evaluate_model(model, test_df):
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    forecast = forecast[["ds", "yhat"]].tail(90).reset_index(drop=True)
    actuals = test_df["y"].values
    predicted = forecast["yhat"].values
    mae = np.mean(np.abs(actuals - predicted))
    rmse = np.sqrt(np.mean((actuals - predicted) ** 2))
    return float(round(mae, 2)), float(round(rmse, 2))

def save_metrics_to_postgres(results):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.model_metrics (
            label TEXT,
            city TEXT,
            ev_network TEXT,
            total_ports INTEGER,
            mae NUMERIC,
            rmse NUMERIC,
            evaluated_at TEXT
        )
    """)
    cursor.execute("DELETE FROM mart.model_metrics")
    for entry in results:
        cursor.execute("""
            INSERT INTO mart.model_metrics
            (label, city, ev_network, total_ports, mae, rmse, evaluated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            entry["label"],
            entry["city"],
            entry["ev_network"],
            entry["total_ports"],
            entry["mae"],
            entry["rmse"],
            entry["evaluated_at"]
        ))
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Metrics saved to mart.model_metrics")

def run():
    registry = load_registry()
    results = []

    for entry in registry:
        label = entry["label"]
        model_path = entry["model_path"]
        total_ports = entry["total_ports"]

        logger.info("Evaluating: " + label)

        model = joblib.load(model_path)
        test_df = generate_test_series(total_ports, seed=total_ports)
        mae, rmse = evaluate_model(model, test_df)

        entry["mae"] = mae
        entry["rmse"] = rmse
        entry["evaluated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        results.append(entry)
        logger.info("MAE: " + str(mae) + " | RMSE: " + str(rmse))

    with open("models/model_registry.json", "w") as f:
        json.dump(results, f, indent=2)

    save_metrics_to_postgres(results)
    logger.info("Evaluation complete. Results saved to models/model_registry.json and mart.model_metrics")

if __name__ == "__main__":
    run()
