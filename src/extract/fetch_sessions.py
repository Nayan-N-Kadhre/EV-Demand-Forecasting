import requests
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NREL_API_KEY = os.getenv("NREL_API_KEY")
BASE_URL = "https://developer.nlr.gov/api/alt-fuel-stations/v1.json"

def fetch_ev_stations(state: str = "CA") -> dict:
    """
    Fetch EV charging station data from NLR API.
    Filters for electric fuel type in a given state.
    """
    params = {
        "api_key": NREL_API_KEY,
        "fuel_type": "ELEC",
        "state": state,
        "limit": "all",
        "status": "E",
        "access": "public"
    }

    logger.info(f"Fetching EV stations for state: {state}")

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()
    station_count = len(data.get("fuel_stations", []))
    logger.info(f"Fetched {station_count} stations")

    return data

def save_raw(data: dict, state: str = "CA") -> str:
    """
    Saves raw API response as a date-stamped JSON file.
    Returns the file path.
    """
    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"data/raw/stations_{state}_{today}.json"

    os.makedirs("data/raw", exist_ok=True)

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Raw data saved to {filename}")
    return filename

def run():
    data = fetch_ev_stations(state="CA")
    save_raw(data, state="CA")

if __name__ == "__main__":
    run()
