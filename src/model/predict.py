import os
import logging
import json
import joblib
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_registry():
    with open("models/model_registry.json", "r") as f:
        return json.load(f)

def generate_forecast(model, periods=7):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)

def run():
    registry = load_registry()
    all_forecasts = []

    for entry in registry:
        label = entry["label"]
        model_path = entry["model_path"]

        logger.info("Generating 7-day forecast for: " + label)

        model = joblib.load(model_path)
        forecast = generate_forecast(model, periods=7)
        forecast["label"] = label
        forecast["city"] = entry["city"]
        forecast["ev_network"] = entry["ev_network"]
        forecast["total_ports"] = entry["total_ports"]

        all_forecasts.append(forecast)

    combined = pd.concat(all_forecasts, ignore_index=True)

    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/forecasts_7day.csv"
    combined.to_csv(output_path, index=False)

    logger.info("Forecasts saved to " + output_path)
    logger.info("Preview:")
    logger.info(combined[["city", "ev_network", "ds", "yhat"]].head(7).to_string())

if __name__ == "__main__":
    run()
