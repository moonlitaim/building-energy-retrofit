"""Air-quality and community data. Default data is SIMULATED."""
import os

import numpy as np
import pandas as pd

import config

# Indian CPCB AQI bands: (upper limit, label, colour, advice)
AQI_BANDS = [
    (50, "Good", "#2e9e4f", "Air is clean. Great day for outdoor activity."),
    (100, "Satisfactory", "#8bc34a", "Fine for most people. Very sensitive people may notice minor effects."),
    (200, "Moderate", "#f4c20d", "People with asthma or heart conditions should reduce long outdoor exertion."),
    (300, "Poor", "#f57c00", "Limit outdoor exercise. Consider a mask outdoors."),
    (400, "Very Poor", "#d32f2f", "Avoid outdoor exertion. Keep windows closed."),
    (500, "Severe", "#7b1fa2", "Stay indoors where possible. Seek medical help if you feel unwell."),
]


def aqi_band(aqi):
    for limit, label, colour, advice in AQI_BANDS:
        if aqi <= limit:
            return label, colour, advice
    return AQI_BANDS[-1][1], AQI_BANDS[-1][2], AQI_BANDS[-1][3]


def sample_neighbourhoods(seed=7):
    rng = np.random.default_rng(seed)
    names = ["Green Park Colony", "Market Road", "Industrial Belt",
             "Lake View Society", "Old Town", "University Campus"]
    base_aqi = [95, 210, 340, 70, 260, 120]
    lat0, lon0 = config.DEFAULT_CENTER
    rows = []
    for name, aqi in zip(names, base_aqi):
        pm25 = round(aqi * 0.45 + rng.normal(0, 4), 1)
        rows.append({
            "name": name,
            "lat": lat0 + rng.uniform(-0.04, 0.04),
            "lon": lon0 + rng.uniform(-0.04, 0.04),
            "aqi": aqi,
            "pm25": max(pm25, 5),
            "pm10": round(aqi * 0.8 + rng.normal(0, 6), 1),
            "no2": round(20 + aqi * 0.15 + rng.normal(0, 3), 1),
            "o3": round(30 + rng.normal(0, 8), 1),
        })
    df = pd.DataFrame(rows)
    df["band"] = df["aqi"].apply(lambda a: aqi_band(a)[0])
    df["color"] = df["aqi"].apply(lambda a: aqi_band(a)[1])
    df["size"] = 350
    return df


def get_live_aqi(lat, lon):
    """OPTIONAL live pollutants from OpenWeather. Needs OPENWEATHER_API_KEY.
    Not tested against the live service. Returns None on any problem."""
    key = os.environ.get("OPENWEATHER_API_KEY")
    if not key:
        return None
    try:
        import requests

        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            params={"lat": lat, "lon": lon, "appid": key},
            timeout=8,
        )
        resp.raise_for_status()
        item = resp.json()["list"][0]
        comp = item["components"]
        return {
            "index_1_to_5": item["main"]["aqi"],
            "pm25": comp.get("pm2_5"),
            "pm10": comp.get("pm10"),
            "no2": comp.get("no2"),
            "o3": comp.get("o3"),
            "timestamp": item.get("dt"),
        }
    except Exception:
        return None


def sample_posts():
    return [
        {"id": 1, "author": "Aarav", "area": "Green Park Colony",
         "text": "Planted 3 saplings near the community garden.", "xp": 40, "likes": 12},
        {"id": 2, "author": "Meera", "area": "Lake View Society",
         "text": "Cut my flat's electricity use by 18 kWh this week.", "xp": 20, "likes": 8},
        {"id": 3, "author": "Kabir", "area": "Market Road",
         "text": "Organised a 20-person clean-up on Sunday morning.", "xp": 40, "likes": 21},
    ]
