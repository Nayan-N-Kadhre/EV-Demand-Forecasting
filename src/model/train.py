import os
import logging
import pandas as pd
import psycopg2
import joblib
import json
import numpy as np
from prophet import Prophet
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "10.255.255.254")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ev_pipeline")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Nayan123@")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_training_data():
    conn = get_connection()
    query = """
        SELECT city, ev_network, total_ports, total_stations, dc_fast_pct
        FROM mart.fct_hourly_demand
        ORDER BY total_ports DESC
        LIMIT 10
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def generate_time_series(row):
    dates = pd.date_range(start="2025-01-01", periods=365, freq="D")
    base = row["total_ports"]
    np.random.seed(int(row["total_ports"]) % 1000)
    weekday_effect = [1.0, 1.0, 1.0, 1.0, 1.1, 1.3, 1.2]
    values = [
        base * weekday_effect[d.weekday()] + np.random.normal(0, base * 0.05)
        for d in dates
    ]
    ts = pd.DataFrame({"ds": dates, "y": values})
    return ts

def train_model(ts):
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )
    model.fit(ts)
    return model

def run():
    os.makedirs("models", exist_ok=True)
    df = get_training_data()
    registry = []

    for _, row in df.iterrows():
        city = row["city"].replace(" ", "_")
        network = row["ev_network"].replace(" ", "_")
        label = city + "_" + network
        logger.info("Training model for: " + label)

        ts = generate_time_series(row)
        model = train_model(ts)

        model_path = "models/prophet_" + label + ".pkl"
        joblib.dump(model, model_path)

        registry.append({
            "label": label,
            "city": row["city"],
            "ev_network": row["ev_network"],
            "total_ports": int(row["total_ports"]),
            "model_path": model_path,
            "trained_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

        logger.info("Model saved to: " + model_path)

    with open("models/model_registry.json", "w") as f:
        json.dump(registry, f, indent=2)

    logger.info("Training complete. " + str(len(registry)) + " models saved.")

if __name__ == "__main__":
    run()
