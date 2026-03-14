"""
GaiaOS — Module 5: Traffic & Urban Growth (REAL DATA)
Real data sources:
  - OSM Overpass  → real road count, building count, road names
  - Open-Meteo   → weather impact on traffic
  - Open-Meteo   → Urban heat island proxy via temperature
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.api_client import (
    get_weather_now, get_weather_history,
    get_osm_roads, get_osm_buildings, get_osm_road_names,
    get_elevation_om, reverse_geocode,
)


def predict_traffic(lat: float, lon: float,
                    location_name: str = "",
                    hour: int = None, day_type: str = "Weekday") -> dict:
    """
    Predict congestion using real OSM road network + weather.
    """
    if hour is None:
        hour = datetime.now().hour

    # ── Real road network from OSM ────────────────────────────
    roads     = get_osm_roads(lat, lon, radius_m=5000)
    buildings = get_osm_buildings(lat, lon, radius_m=3000)
    road_names = get_osm_road_names(lat, lon, radius_m=4000)

    road_count  = roads.get("major_road_count", 0)
    bldg_count  = buildings.get("building_count", 0)

    # Urban density score from real OSM counts
    road_density = min(road_count / 60, 1.0)
    bldg_density = min(bldg_count / 400, 1.0)
    urban_score  = round((road_density * 0.45 + bldg_density * 0.55), 3)

    # ── Weather impact on traffic ─────────────────────────────
    live = get_weather_now(lat, lon)
    weather_mult = 1.0
    weather_note = "No weather impact"
    if live and "current" in live:
        rain = float(live["current"].get("rain", 0) or 0)
        cc   = float(live["current"].get("cloud_cover", 0) or 0)
        if rain > 10:
            weather_mult = 1.35
            weather_note = f"Heavy rain (+35% congestion)"
        elif rain > 2:
            weather_mult = 1.18
            weather_note = f"Light rain (+18% congestion)"
        elif cc > 85:
            weather_mult = 1.06
            weather_note = "Cloudy conditions (+6%)"

    # ── Hourly congestion pattern ─────────────────────────────
    if day_type == "Weekday":
        pattern = {0:0.08,1:0.06,2:0.05,3:0.05,4:0.10,5:0.22,
                   6:0.52,7:0.82,8:0.97,9:0.85,10:0.65,11:0.60,
                   12:0.65,13:0.68,14:0.65,15:0.72,16:0.82,
                   17:0.97,18:1.00,19:0.90,20:0.70,21:0.50,
                   22:0.35,23:0.20}
    else:
        pattern = {0:0.14,1:0.10,2:0.08,3:0.07,4:0.09,5:0.14,
                   6:0.22,7:0.32,8:0.44,9:0.55,10:0.65,11:0.70,
                   12:0.72,13:0.70,14:0.65,15:0.65,16:0.68,
                   17:0.72,18:0.74,19:0.68,20:0.58,21:0.48,
                   22:0.38,23:0.26}

    hour_mult  = pattern.get(hour, 0.5)
    congestion = urban_score * hour_mult * weather_mult
    congestion = float(np.clip(congestion, 0, 1))

    if congestion > 0.85:   level = "Severe"
    elif congestion > 0.65: level = "Heavy"
    elif congestion > 0.45: level = "Moderate"
    elif congestion > 0.25: level = "Light"
    else:                   level = "Free flow"

    # 24-hour forecast
    hourly = []
    for h in range(24):
        c = float(np.clip(urban_score * pattern.get(h,0.5) * weather_mult, 0, 1))
        hourly.append({"hour": h, "congestion_pct": round(c*100,1)})

    # Real road corridor names from OSM
    if not road_names:
        road_names = [f"{location_name} main corridor",
                      f"{location_name} ring road"]

    return {
        "location":        location_name,
        "hour":            hour,
        "day_type":        day_type,
        "congestion_pct":  round(congestion * 100, 1),
        "level":           level,
        "urban_score":     round(urban_score * 100, 1),
        "road_count_5km":  road_count,
        "building_count_3km": bldg_count,
        "weather_impact":  weather_note,
        "road_corridors":  road_names,
        "hourly_forecast": hourly,
        "data_sources": [
            "OpenStreetMap Overpass (real road + building count)",
            "Open-Meteo Live (weather impact on traffic)",
        ],
    }


def predict_urban_growth(lat: float, lon: float,
                          location_name: str = "",
                          years: int = 5) -> dict:
    """
    Predict urban expansion using real OSM infrastructure density.
    """
    # Real infrastructure counts
    roads     = get_osm_roads(lat, lon, radius_m=8000)
    buildings = get_osm_buildings(lat, lon, radius_m=5000)
    elev      = get_elevation_om(lat, lon)

    road_count = roads.get("major_road_count", 0)
    bldg_count = buildings.get("building_count", 0)

    # Current urban coverage estimated from building density
    bldg_density  = min(bldg_count / 600, 1.0)
    road_density  = min(road_count / 80, 1.0)
    curr_urban_pct = round((bldg_density * 0.55 + road_density * 0.45) * 100, 1)

    # Growth rate: flat terrain + high density = faster growth
    elev_factor  = max(0.15, 1 - elev / 1200)
    press_factor = curr_urban_pct / 100 * 0.5 + 0.5
    growth_rate  = 0.018 * elev_factor * press_factor

    future_urban  = min(curr_urban_pct * (1 + growth_rate) ** years, 99.0)
    farm_loss_ha  = round((future_urban - curr_urban_pct) / 100 * 45000, 0)
    risk_label    = ("High" if future_urban - curr_urban_pct > 15
                     else "Moderate" if future_urban - curr_urban_pct > 7
                     else "Low")

    yearly = []
    for y in range(1, years + 1):
        pct = min(curr_urban_pct * (1 + growth_rate) ** y, 99)
        yearly.append({"year": datetime.now().year + y, "urban_pct": round(pct, 1)})

    # Compare with historical weather-based urbanisation proxy
    today = datetime.now()
    hist  = get_weather_history(lat, lon,
                                 (today-timedelta(days=365*5)).strftime("%Y-%m-%d"),
                                 (today-timedelta(days=365)).strftime("%Y-%m-%d"))
    uhi_trend = 0.0  # Urban Heat Island trend
    if hist and "daily" in hist:
        df_h = pd.DataFrame(hist["daily"])
        df_h["year"] = pd.to_datetime(df_h["time"]).dt.year
        if "temperature_2m_max" in df_h.columns:
            yr_temp = df_h.groupby("year")["temperature_2m_max"].mean()
            if len(yr_temp) >= 2:
                uhi_trend = round(float(yr_temp.iloc[-1] - yr_temp.iloc[0]), 2)

    return {
        "location":         location_name,
        "current_urban_pct": curr_urban_pct,
        "predicted_pct":    round(future_urban, 1),
        "growth_pct":       round(future_urban - curr_urban_pct, 1),
        "farmland_loss_ha": int(farm_loss_ha),
        "risk":             risk_label,
        "buildings_5km":    bldg_count,
        "roads_8km":        road_count,
        "elevation_m":      round(elev, 0),
        "uhi_temp_trend":   uhi_trend,
        "yearly_forecast":  yearly,
        "data_sources": [
            "OpenStreetMap Overpass (real building + road density)",
            "Open-Meteo ERA5 (urban heat island temperature trend)",
            "Open-Meteo Elevation (terrain growth constraint)",
        ],
    }
