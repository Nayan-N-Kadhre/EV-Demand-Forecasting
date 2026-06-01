import os
import logging
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    return round(mae, 2), round(rmse, 2)

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
        entry["evaluated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        results.append(entry)
        logger.info("MAE: " + str(mae) + " | RMSE: " + str(rmse))

    with open("models/model_registry.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("Evaluation complete. Results saved to models/model_registry.json")

if __name__ == "__main__":
    run()
