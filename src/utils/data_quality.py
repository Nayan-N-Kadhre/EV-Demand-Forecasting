import logging
import psycopg2
import os
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

def run_checks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.dq_log (
            check_name TEXT,
            status TEXT,
            detail TEXT,
            checked_at TIMESTAMPTZ
        )
    """)

    checks = [
        ("raw_row_count", "SELECT COUNT(*) FROM raw.ev_stations", 19000),
        ("staging_row_count", "SELECT COUNT(*) FROM staging.stg_stations", 10000),
        ("mart_row_count", "SELECT COUNT(*) FROM mart.fct_hourly_demand", 100),
        ("staging_null_station_id", "SELECT COUNT(*) FROM staging.stg_stations WHERE station_id IS NULL", 0),
        ("staging_null_latitude", "SELECT COUNT(*) FROM staging.stg_stations WHERE latitude IS NULL", 0),
    ]

    for check_name, query, threshold in checks:
        cursor.execute(query)
        result = cursor.fetchone()[0]

        if check_name.startswith("staging_null"):
            status = "PASS" if result == threshold else "FAIL"
            detail = "null count: " + str(result)
        else:
            status = "PASS" if result >= threshold else "FAIL"
            detail = "row count: " + str(result)

        cursor.execute("""
            INSERT INTO raw.dq_log (check_name, status, detail, checked_at)
            VALUES (%s, %s, %s, %s)
        """, (check_name, status, detail, datetime.now(timezone.utc)))

        logger.info(check_name + " -> " + status + " | " + detail)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Data quality checks complete")

if __name__ == "__main__":
    run_checks()
