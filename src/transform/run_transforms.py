import os
import logging
import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "10.255.255.254")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ev_pipeline")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "REDACTED_PASSWORD")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQL_FILES = [
    os.path.join(BASE_DIR, "sql/staging/stg_stations.sql"),
    os.path.join(BASE_DIR, "sql/mart/fct_hourly_demand.sql"),
]

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def run_sql_file(conn, filepath):
    with open(filepath, "r") as f:
        sql = f.read()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    logger.info("Executed: " + filepath)

def run():
    conn = get_connection()
    try:
        for sql_file in SQL_FILES:
            run_sql_file(conn, sql_file)
        logger.info("All transforms completed successfully")
    finally:
        conn.close()

if __name__ == "__main__":
    run()
