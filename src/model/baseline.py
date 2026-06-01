import os
import logging
import pandas as pd
import psycopg2
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

def compute_baseline():
    """
    Computes a simple baseline: rolling 7-day average of total_ports
    grouped by city and ev_network from the mart layer.
    """
    conn = get_connection()

    query = """
        SELECT
            city,
            state,
            ev_network,
            total_stations,
            total_ports,
            dc_fast_pct,
            level2_pct
        FROM mart.fct_hourly_demand
        ORDER BY total_ports DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df["rolling_avg_ports"] = (
        df.groupby("ev_network")["total_ports"]
        .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
        .round(2)
    )

    logger.info("Baseline computed for " + str(len(df)) + " records")
    logger.info("Top 5 cities by total ports:")
    logger.info(df[["city", "ev_network", "total_ports", "rolling_avg_ports"]].head().to_string())

    return df

def run():
    df = compute_baseline()
    output_path = "data/processed/baseline_results.csv"
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Baseline results saved to " + output_path)

if __name__ == "__main__":
    run()
