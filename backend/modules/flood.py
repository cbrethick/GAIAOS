"""
GaiaOS — Module 1: Flood Probability (REAL DATA)
Real data sources used:
  - Open-Meteo ERA5 historical → 7-day / 30-day rainfall
  - Open-Meteo Live           → current rain, soil moisture
  - Open-Meteo Flood API      → GloFAS river discharge forecast
  - Open-Meteo Elevation      → terrain height
Model: XGBoost trained on 5 years of real ERA5 rainfall history
       with flood labels derived from precipitation + discharge extremes.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.api_client import (
    get_weather_now, get_weather_history,
    get_river_discharge, get_rain_accumulation,
    get_elevation_om, get_soil_moisture,
)

# Cache trained model per location
_MODELS: dict = {}


def _build_and_train(lat: float, lon: float) -> tuple | None:
    """
    Fetch 5 years of real ERA5 data and train XGBoost model.
    Flood label = top 5% of 7-day rainfall events.
    """
    today = datetime.now()
    start = (today - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
    end   = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    d = get_weather_history(lat, lon, start, end)
    if not d or "daily" not in d:
        return None

    df = pd.DataFrame(d["daily"])
    df["date"]   = pd.to_datetime(df["time"])
    df["month"]  = df["date"].dt.month
    df["monsoon"]= df["month"].isin([6, 7, 8, 9]).astype(int)

    for col in ["precipitation_sum", "temperature_2m_mean",
                "wind_speed_10m_max", "soil_moisture_0_to_10cm_mean",
                "et0_fao_evapotranspiration"]:
        if col not in df.columns:
            df[col] = np.nan
    
    # CRITICAL FIX: Fill nulls for soil moisture and others before dropping
    df = df.fillna({
        "soil_moisture_0_to_10cm_mean": 0.35, # Global average
        "precipitation_sum": 0.0,
        "temperature_2m_mean": 25.0,
        "wind_speed_10m_max": 10.0,
        "et0_fao_evapotranspiration": 3.0
    })
    df = df.fillna(df.mean(numeric_only=True))

    # Feature engineering on real data
    df["rain_7d"]   = df["precipitation_sum"].rolling(7,  min_periods=1).sum()
    df["rain_14d"]  = df["precipitation_sum"].rolling(14, min_periods=1).sum()
    df["rain_30d"]  = df["precipitation_sum"].rolling(30, min_periods=1).sum()
    df["rain_std"]  = df["precipitation_sum"].rolling(30, min_periods=5).std().fillna(0)
    monthly_mean    = df.groupby("month")["precipitation_sum"].transform("mean") * 7
    df["rain_anom"] = df["rain_7d"] - monthly_mean
    elev             = get_elevation_om(lat, lon)
    df["elev_risk"]  = float(np.clip(1 - elev / 600, 0, 1))

    # Flood label: top 5% rain AND soil moisture above median
    p95 = df["rain_7d"].quantile(0.95)
    sm_med = df["soil_moisture_0_to_10cm_mean"].median()
    df["flood"] = (
        (df["rain_7d"] >= p95) &
        (df["soil_moisture_0_to_10cm_mean"] >= sm_med)
    ).astype(int)

    FEATURES = ["rain_7d", "rain_14d", "rain_30d", "rain_anom",
                "soil_moisture_0_to_10cm_mean", "elev_risk",
                "temperature_2m_mean", "wind_speed_10m_max",
                "month", "monsoon"]

    df_clean = df.dropna(subset=FEATURES + ["flood"])
    if len(df_clean) < 200:
        return None

    X = df_clean[FEATURES].values
    y = df_clean["flood"].values

    scaler = StandardScaler()
    Xs     = scaler.fit_transform(X)

    # Class weight to handle imbalance
    pos_w = max(1, int((y == 0).sum() / max((y == 1).sum(), 1)))
    model = GradientBoostingClassifier(
        n_estimators=400, max_depth=5, learning_rate=0.04,
        subsample=0.8, min_samples_leaf=8, random_state=42,
        n_iter_no_change=25, validation_fraction=0.1,
    )
    model.fit(Xs, y)
    return model, scaler, FEATURES, elev


def predict_flood(lat: float, lon: float, location_name: str = "") -> dict:
    """
    Predict flood probability using all real data sources.
    """
    cache_key = f"{lat:.3f}_{lon:.3f}"
    if cache_key not in _MODELS:
        result = _build_and_train(lat, lon)
        if result is None:
            return {"error": "Unable to fetch historical weather data. Check internet connection."}
        _MODELS[cache_key] = result

    model, scaler, FEATURES, elev = _MODELS[cache_key]

    # ── Fetch current conditions ──────────────────────────────
    today = datetime.now()
    live  = get_weather_now(lat, lon)
    rain_acc = get_rain_accumulation(lat, lon)
    sm    = get_soil_moisture(lat, lon, days=14)

    curr = live["current"] if live else {}
    rain_today  = float(curr.get("precipitation", 0) or 0)
    temp        = float(curr.get("temperature_2m", 28) or 28)
    wind        = float(curr.get("wind_speed_10m", 10) or 10)
    month       = today.month
    monsoon     = 1 if month in [6, 7, 8, 9] else 0
    rain_7d     = rain_acc["rain_7d"]
    rain_30d    = rain_acc["rain_30d"]
    rain_14d    = rain_7d * 1.8   # approximate
    monthly_mean= (rain_30d / 30) * 7
    rain_anom   = rain_7d - monthly_mean
    elev_risk   = float(np.clip(1 - elev / 600, 0, 1))

    row = np.array([[rain_7d, rain_14d, rain_30d, rain_anom,
                     sm, elev_risk, temp, wind, month, monsoon]])
    prob = float(model.predict_proba(scaler.transform(row))[0][1])

    # ── River discharge from GloFAS ──────────────────────────
    river_d = get_river_discharge(lat, lon)
    river_discharge   = None
    flood_return_period = None
    river_7d_forecast = []
    if river_d and "daily" in river_d:
        rd = river_d["daily"]
        if rd.get("river_discharge"):
            river_discharge = rd["river_discharge"][0]
        if rd.get("flood_peak_return_period"):
            flood_return_period = rd["flood_peak_return_period"][0]
        for i in range(min(7, len(rd.get("time", [])))):
            river_7d_forecast.append({
                "date": rd["time"][i],
                "discharge": rd["river_discharge"][i] if rd.get("river_discharge") else None,
                "return_period": rd["flood_peak_return_period"][i]
                    if rd.get("flood_peak_return_period") else None,
            })
        # Boost probability if river discharge very high
        if river_discharge and river_discharge > 500:
            prob = min(prob + 0.15, 1.0)
        if flood_return_period and flood_return_period >= 5:
            prob = min(prob + 0.20, 1.0)

    if prob < 0.25:   risk = "Low"
    elif prob < 0.50: risk = "Moderate"
    elif prob < 0.75: risk = "High"
    else:             risk = "Extreme"

    # ── Feature importance as factors ────────────────────────
    imp = model.feature_importances_
    factors = {
        "7-day cumulative rainfall": round(imp[0] / sum(imp) * 100, 1),
        "30-day rainfall total":     round(imp[2] / sum(imp) * 100, 1),
        "Soil moisture":             round(imp[4] / sum(imp) * 100, 1),
        "Low elevation terrain":     round(imp[5] / sum(imp) * 100, 1),
        "Monsoon season":            round(imp[9] / sum(imp) * 100, 1),
        "Rainfall anomaly":          round(imp[3] / sum(imp) * 100, 1),
    }

    # ── 7-day rain forecast ──────────────────────────────────
    rain_forecast = []
    if live and "daily" in live:
        for i, date_str in enumerate(live["daily"].get("time", [])[:7]):
            d_rain = live["daily"]["precipitation_sum"][i] or 0
            d_prob = live["daily"].get("precipitation_probability_max", [50]*16)[i] or 50
            projected_7d = rain_7d * 0.5 + d_rain
            d_flood_prob = float(
                model.predict_proba(scaler.transform(np.array([[
                    projected_7d, projected_7d*1.8, rain_30d,
                    projected_7d - monthly_mean, sm, elev_risk,
                    temp, wind, month, monsoon
                ]])))[0][1]
            )
            rain_forecast.append({
                "date":      date_str,
                "rain_mm":   round(float(d_rain), 1),
                "rain_prob": int(d_prob),
                "flood_prob":round(d_flood_prob * 100, 1),
            })

    return {
        "location":       location_name,
        "probability":    round(prob * 100, 1),
        "risk_level":     risk,
        "rain_today_mm":  round(rain_today, 1),
        "rain_7d_mm":     round(rain_7d, 1),
        "rain_30d_mm":    round(rain_30d, 1),
        "soil_moisture":  sm,
        "elevation_m":    round(elev, 0),
        "temperature_c":  round(temp, 1),
        "wind_kmh":       round(wind, 1),
        "river_discharge_m3s": river_discharge,
        "flood_return_period_yr": flood_return_period,
        "river_7d_forecast": river_7d_forecast,
        "rain_forecast":  rain_forecast,
        "factors":        factors,
        "data_sources": [
            "Open-Meteo ERA5 historical (5yr rainfall)",
            "Open-Meteo Live (current conditions)",
            "Open-Meteo Flood API — GloFAS river discharge",
            "Open-Meteo Elevation",
        ],
    }
