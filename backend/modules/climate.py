"""
GaiaOS — Module 2: Climate Patterns (REAL DATA)
Real data sources:
  - Open-Meteo ERA5 archive → 30-year climate normals
  - Open-Meteo Live         → current + 16-day forecast
  - Open-Meteo Air Quality  → pollution/AQI
Outputs: temp anomaly, SPI drought index, monsoon prediction, 16-day forecast.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.api_client import (
    get_weather_now, get_weather_history, get_air_quality
)

# India state → monsoon normal onset date
INDIA_MONSOON_ONSET = {
    "Kerala":           (6, 1),   "Tamil Nadu":        (6, 1),
    "Karnataka":        (6, 5),   "Goa":               (6, 5),
    "Maharashtra":      (6, 10),  "Andhra Pradesh":    (6, 12),
    "Telangana":        (6, 15),  "Odisha":            (6, 10),
    "West Bengal":      (6, 7),   "Assam":             (5, 25),
    "Arunachal Pradesh":(5, 20),  "Meghalaya":         (5, 22),
    "Bihar":            (6, 20),  "Jharkhand":         (6, 15),
    "Uttar Pradesh":    (6, 25),  "Rajasthan":         (7, 1),
    "Gujarat":          (6, 20),  "Madhya Pradesh":    (6, 20),
    "Chhattisgarh":     (6, 15),  "Punjab":            (7, 1),
    "Haryana":          (7, 1),   "Delhi":             (6, 29),
    "Himachal Pradesh": (7, 1),   "Uttarakhand":       (6, 25),
    "Jammu and Kashmir":(7, 1),   "Ladakh":            (7, 15),
}


def _spi_index(monthly_rain_list: list, normal_monthly_rain: float) -> tuple:
    """Compute SPI-3 drought index."""
    if not monthly_rain_list or normal_monthly_rain == 0:
        return 0.0, "Normal"
    series  = np.array(monthly_rain_list)
    recent  = np.mean(series[-3:]) if len(series) >= 3 else np.mean(series)
    std     = np.std(series) if len(series) > 2 else normal_monthly_rain * 0.35
    std     = max(std, 1.0)
    spi     = (recent - normal_monthly_rain) / std
    if spi >= 2.0:      label = "Extremely wet"
    elif spi >= 1.0:    label = "Moderately wet"
    elif spi >= -0.49:  label = "Normal"
    elif spi >= -0.99:  label = "Mildly dry"
    elif spi >= -1.49:  label = "Moderate drought"
    elif spi >= -1.99:  label = "Severe drought"
    else:               label = "Extreme drought"
    return round(float(spi), 2), label


def predict_climate(lat: float, lon: float,
                    state: str = "", location_name: str = "") -> dict:
    """
    Predict climate indicators using real ERA5 + live forecast.
    """
    today = datetime.now()
    month = today.month

    # ── Live weather + 16-day forecast ───────────────────────
    live = get_weather_now(lat, lon)
    if not live:
        return {"error": "Weather API unavailable. Check internet connection."}

    curr      = live["current"]
    curr_temp = float(curr.get("temperature_2m", 0) or 0)
    curr_hum  = float(curr.get("relative_humidity_2m", 70) or 70)
    curr_rain = float(curr.get("rain", 0) or 0)

    # ── ERA5 historical normals (10 years, faster than 30yr) ─
    hist = get_weather_history(
        lat, lon,
        (today - timedelta(days=365*10)).strftime("%Y-%m-%d"),
        (today - timedelta(days=366)).strftime("%Y-%m-%d"),
    )

    monthly_normals = {}
    monthly_rain_by_year = {}
    if hist and "daily" in hist:
        df_h = pd.DataFrame(hist["daily"])
        df_h["date"]  = pd.to_datetime(df_h["time"])
        df_h["month"] = df_h["date"].dt.month
        df_h["year"]  = df_h["date"].dt.year
        for m in range(1, 13):
            sub = df_h[df_h["month"] == m]
            monthly_normals[m] = {
                "temp": float(sub["temperature_2m_mean"].mean())
                        if "temperature_2m_mean" in sub.columns else 25.0,
                "rain": float(sub["precipitation_sum"].mean())
                        if "precipitation_sum" in sub.columns else 3.0,
            }
        # Monthly totals per year (for SPI)
        monthly_totals = df_h[df_h["month"] == month].groupby("year")["precipitation_sum"].sum()
        monthly_rain_by_year = monthly_totals.tolist()

    normal_temp = monthly_normals.get(month, {}).get("temp", 28.0)
    normal_rain = monthly_normals.get(month, {}).get("rain", 3.0) * 30
    temp_anomaly = round(curr_temp - normal_temp, 2)

    # ── SPI drought index ─────────────────────────────────────
    spi, drought_label = _spi_index(monthly_rain_by_year, normal_rain)

    # ── Monsoon onset prediction ──────────────────────────────
    onset   = INDIA_MONSOON_ONSET.get(state, (7, 1))
    try:
        onset_date   = datetime(today.year, onset[0], onset[1])
    except ValueError:
        onset_date   = datetime(today.year, 7, 1)
    days_to = (onset_date - today).days

    # Adjust onset by temperature anomaly (warmer ocean → delayed)
    if temp_anomaly > 0.8:
        days_to += int(temp_anomaly * 3)
    elif temp_anomaly < -0.8:
        days_to -= int(abs(temp_anomaly) * 2)

    is_monsoon = (month >= onset[0] and month <= onset[0] + 3)
    if is_monsoon:
        if curr_rain > 3 or curr_hum > 78:
            monsoon_status = "Active monsoon"
        else:
            monsoon_status = "Monsoon season (currently weak)"
    elif days_to <= 0:
        monsoon_status = "Monsoon has arrived"
    elif days_to <= 12:
        monsoon_status = f"Monsoon arriving in ~{max(0,days_to)} days"
    elif days_to <= 50:
        monsoon_status = f"Monsoon expected in ~{days_to} days"
    else:
        monsoon_status = "Off-season (pre/post monsoon)"

    # ── 16-day forecast table ────────────────────────────────
    forecast = []
    if live and "daily" in live:
        daily = live["daily"]
        for i, date_str in enumerate(daily.get("time", [])):
            tmax  = daily["temperature_2m_max"][i] or 0
            tmin  = daily["temperature_2m_min"][i] or 0
            tmean = round((tmax + tmin) / 2, 1)
            f_m   = pd.to_datetime(date_str).month
            f_norm = monthly_normals.get(f_m, {}).get("temp", 28.0)
            forecast.append({
                "date":    date_str,
                "tmax":    round(tmax, 1),
                "tmin":    round(tmin, 1),
                "tmean":   tmean,
                "anomaly": round(tmean - f_norm, 1),
                "rain_mm": round(daily["precipitation_sum"][i] or 0, 1),
                "rain_prob": daily.get("precipitation_probability_max",[50]*17)[i] or 0,
            })

    # ── Air quality ──────────────────────────────────────────
    aq_data = get_air_quality(lat, lon)
    aqi = {}
    if aq_data and "current" in aq_data:
        aqc = aq_data["current"]
        aqi = {
            "pm2_5":   aqc.get("pm2_5"),
            "pm10":    aqc.get("pm10"),
            "no2":     aqc.get("nitrogen_dioxide"),
            "so2":     aqc.get("sulphur_dioxide"),
            "o3":      aqc.get("ozone"),
            "dust":    aqc.get("dust"),
            "uv":      aqc.get("uv_index"),
            "us_aqi":  aqc.get("us_aqi"),
            "eu_aqi":  aqc.get("european_aqi"),
        }
        # Remove None values
        aqi = {k: v for k, v in aqi.items() if v is not None}

    return {
        "location":       location_name,
        "current_temp":   round(curr_temp, 1),
        "humidity":       round(curr_hum, 1),
        "temp_anomaly":   temp_anomaly,
        "anomaly_label":  f"{'+' if temp_anomaly>0 else ''}{temp_anomaly}°C vs 10yr normal",
        "normal_temp":    round(normal_temp, 1),
        "normal_rain_mm": round(normal_rain, 1),
        "spi":            spi,
        "drought_label":  drought_label,
        "monsoon_status": monsoon_status,
        "forecast_16d":   forecast,
        "air_quality":    aqi,
        "data_sources": [
            "Open-Meteo ERA5 (10yr climate normals)",
            "Open-Meteo Live (current + 16-day forecast)",
            "Open-Meteo Air Quality (Copernicus CAMS)",
        ],
    }
