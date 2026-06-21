import json
import os
import logging
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timezone

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

def get_latest_raw_file(state="CA"):
    raw_dir = "data/raw"
    files = [f for f in os.listdir(raw_dir) if f.startswith("stations_" + state + "_") and f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No raw files found for state: " + state)
    latest = sorted(files)[-1]
    path = os.path.join(raw_dir, latest)
    logger.info("Loading raw file: " + path)
    return path

def load_to_postgres(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    stations = data.get("fuel_stations", [])
    if not stations:
        raise ValueError("No stations found in raw file")

    df = pd.DataFrame(stations)
    df["ingested_at"] = datetime.now(timezone.utc)

    df = df.astype(str)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")

    columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
    cursor.execute(f"DROP TABLE IF EXISTS raw.ev_stations")
    cursor.execute(f"CREATE TABLE raw.ev_stations ({columns})")

    for _, row in df.iterrows():
        placeholders = ", ".join(["%s"] * len(row))
        cursor.execute(
            f"INSERT INTO raw.ev_stations VALUES ({placeholders})",
            list(row)
        )

    conn.commit()
    cursor.close()
    conn.close()

    logger.info("Loaded " + str(len(df)) + " stations into raw.ev_stations")

def run():
    filepath = get_latest_raw_file(state="CA")
    load_to_postgres(filepath)

if __name__ == "__main__":
    run()
