"""Building energy model: predicts expected use and flags retrofit candidates."""
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_predict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample.csv")
FEATURES = ["floor_area", "age", "occupancy", "avg_temp", "building_type"]


def generate_sample_data(n=200, seed=42):
    """Creates SIMULATED building data (monthly energy in kWh)."""
    rng = np.random.default_rng(seed)
    types = rng.choice(["Office", "School", "Hospital", "Residential"], size=n)
    floor_area = rng.integers(500, 10000, size=n)
    age = rng.integers(1, 60, size=n)
    occupancy = rng.integers(10, 800, size=n)
    avg_temp = rng.normal(28, 4, size=n).round(1)

    type_factor = (
        pd.Series(types)
        .map({"Office": 1.0, "School": 0.8, "Hospital": 1.8, "Residential": 0.6})
        .to_numpy()
    )
    base = (floor_area * 8 + occupancy * 20 + age * 40 + (avg_temp - 20) * 60) * type_factor
    actual = base * rng.normal(1, 0.05, size=n)

    # About 15% of buildings waste energy: these are the retrofit candidates.
    wasteful = rng.random(n) < 0.15
    actual = np.where(wasteful, actual * rng.uniform(1.3, 1.7, size=n), actual)

    return pd.DataFrame({
        "building_id": [f"B{i:03d}" for i in range(1, n + 1)],
        "building_type": types,
        "floor_area": floor_area,
        "age": age,
        "occupancy": occupancy,
        "avg_temp": avg_temp,
        "actual_kwh": actual.round(0),
    })


def load_data():
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        generate_sample_data().to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)


def run_model(df):
    X = pd.get_dummies(df[FEATURES], columns=["building_type"])
    y = df["actual_kwh"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    predicted = cross_val_predict(model, X, y, cv=5)

    result = df.copy()
    result["predicted_kwh"] = predicted.round(0)
    result["excess_pct"] = ((y - predicted) / predicted * 100).round(1)
    score = r2_score(y, predicted)
    return result, score
