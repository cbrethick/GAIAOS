"""
GaiaOS — Module 4: Wildfire Risk (REAL DATA)
Real data sources:
  - Open-Meteo Live  → temperature, humidity, wind (FWI inputs)
  - NASA FIRMS       → real active fire detections (VIIRS + MODIS)
  - Open-Meteo AQ    → dust + PM10 (smoke proxy)
Model: Canadian Fire Weather Index (standard operational system).
"""

import numpy as np
import pandas as pd
import math
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.api_client import (
    get_weather_now, get_weather_history,
    get_firms_fires, get_air_quality,
    get_elevation_om,
)

DANGER_CLASSES = {
    "Low":       {"range": (0,  5),  "color": "#22c55e"},
    "Moderate":  {"range": (5,  15), "color": "#eab308"},
    "High":      {"range": (15, 30), "color": "#f97316"},
    "Very High": {"range": (30, 50), "color": "#ef4444"},
    "Extreme":   {"range": (50, 999),"color": "#7f1d1d"},
}

def _fwi_ffmc(temp, rh, wind, rain, prev=85.0):
    mo = 147.2 * (101 - prev) / (59.5 + prev)
    if rain > 0.5:
        rf = rain - 0.5
        if mo > 150:
            mo += 42.5 * rf * math.exp(-100/(251-mo)) * (1 - math.exp(-6.93/rf)) + 0.0015*(mo-150)**2 * rf**0.5
        else:
            mo += 42.5 * rf * math.exp(-100/(251-mo)) * (1 - math.exp(-6.93/rf))
    mo = min(mo, 250)
    ed = 0.942*(rh**0.679) + 11*math.exp((rh-100)/10) + 0.18*(21.1-temp)*(1-math.exp(-0.115*rh))
    ew = 0.618*(rh**0.753) + 10*math.exp((rh-100)/10) + 0.18*(21.1-temp)*(1-math.exp(-0.115*rh))
    if mo > ed:
        ko = 0.424*(1-(rh/100)**1.7) + 0.0694*(wind**0.5)*(1-(rh/100)**8)
        kd = ko * 0.581 * math.exp(0.0365*temp)
        m  = ed + (mo-ed) * 10**(-kd)
    elif mo < ew:
        kl = 0.424*(1-((100-rh)/100)**1.7) + 0.0694*(wind**0.5)*(1-((100-rh)/100)**8)
        kw = kl * 0.581 * math.exp(0.0365*temp)
        m  = ew - (ew-mo) * 10**(-kw)
    else:
        m = mo
    return round(max(0, min(101, 59.5*(250-m)/(147.2+m))), 2)

def _fwi_dmc(temp, rh, rain, month, prev=6.0):
    el = {1:6.5,2:7.5,3:9.0,4:12.8,5:13.9,6:13.9,
          7:12.4,8:10.9,9:9.4,10:8.0,11:7.0,12:6.0}.get(month, 9.0)
    if rain > 1.5:
        re  = 0.92*rain - 1.27
        mo  = 20 + math.exp(5.6348 - prev/43.43)
        b   = (100/(0.5+0.3*prev) if prev <= 33 else
               14 - 1.3*math.log(prev) if prev <= 65 else
               6.2*math.log(prev) - 17.2)
        mr  = mo + 1000*re/(48.77 + b*re)
        pr  = max(0, 244.72 - 43.43*math.log(max(mr-20, 0.01)))
        prev = pr
    k = 1.894*(temp+1.1)*(100-rh)*el*1e-6
    return round(max(0, prev + 100*k), 2)

def _fwi_isi(ffmc, wind):
    fm  = 147.2*(101-ffmc)/(59.5+ffmc)
    fw  = math.exp(0.05039*wind)
    ff  = 91.9*math.exp(-0.1386*fm)*(1+(fm**5.31)/4.93e7)
    return round(0.208*fw*ff, 2)

def _fwi_bui(dmc, dc=200.0):
    if dmc <= 0.4*dc:
        return round(0.8*dmc*dc/(dmc+0.4*dc), 2)
    return round(dmc - (1-0.8*dc/(dmc+0.4*dc))*(0.92+(0.0114*dmc)**1.7), 2)

def _fwi_final(isi, bui):
    fd  = 0.626*bui**0.809 + 2 if bui < 80 else 1000/(25+108.64*math.exp(-0.023*bui))
    b   = 0.1*isi*fd
    if b > 1:
        fwi = math.exp(2.72*(0.434*math.log(b))**0.647)
    else:
        fwi = b
    return round(min(fwi, 120), 1)

def _danger_class(fwi: float) -> tuple:
    for cls, info in DANGER_CLASSES.items():
        lo, hi = info["range"]
        if lo <= fwi < hi:
            return cls, info["color"]
    return "Extreme", "#7f1d1d"


def predict_wildfire(lat: float, lon: float,
                     location_name: str = "") -> dict:
    """
    Predict wildfire risk using real Open-Meteo + NASA FIRMS data.
    """
    today = datetime.now()
    month = today.month

    # ── Live weather ─────────────────────────────────────────
    live = get_weather_now(lat, lon)
    if not live:
        return {"error": "Weather API unavailable"}

    c     = live["current"]
    temp  = float(c.get("temperature_2m", 30) or 30)
    rh    = float(c.get("relative_humidity_2m", 40) or 40)
    wind  = float(c.get("wind_speed_10m", 15) or 15)
    rain  = float(c.get("rain", 0) or 0)
    elev  = get_elevation_om(lat, lon)

    # ── Canadian FWI calculation ──────────────────────────────
    ffmc = _fwi_ffmc(temp, rh, wind, rain)
    dmc  = _fwi_dmc(temp, rh, rain, month)
    isi  = _fwi_isi(ffmc, wind)
    bui  = _fwi_bui(dmc)
    fwi  = _fwi_final(isi, bui)

    # India seasonal adjustment
    if month in [3, 4, 5]:     fwi = min(fwi * 1.35, 120)  # peak season
    elif month in [6, 7, 8, 9]: fwi = fwi * 0.45            # monsoon
    elif month in [10, 11]:     fwi = fwi * 1.15

    # Elevation: hill forests burn more
    if elev > 600:
        fwi = min(fwi * 1.1, 120)

    danger, d_color = _danger_class(fwi)

    # ── NASA FIRMS active fires ───────────────────────────────
    fires_df   = get_firms_fires(lat, lon, radius_km=250, days=7)
    fire_count = len(fires_df)
    fire_rows  = []
    if not fires_df.empty:
        # Boost FWI if real fires detected nearby
        fwi = min(fwi * (1 + 0.05 * min(fire_count, 10)), 120)
        danger, d_color = _danger_class(fwi)
        for _, row in fires_df.head(10).iterrows():
            fire_rows.append({
                "lat":   float(row.get("latitude", 0)),
                "lon":   float(row.get("longitude", 0)),
                "date":  str(row.get("acq_date", "")),
                "brightness": float(row.get("bright_ti4",
                                  row.get("brightness", 310))),
                "frp":   float(row.get("frp", 0)),
                "confidence": str(row.get("confidence", "nominal")),
            })

    # ── Air quality (smoke/dust) ──────────────────────────────
    aq   = get_air_quality(lat, lon)
    dust = pm10 = None
    if aq and "current" in aq:
        dust = aq["current"].get("dust")
        pm10 = aq["current"].get("pm10")

    # ── 7-day forecast ────────────────────────────────────────
    forecast_7d = []
    if live and "daily" in live:
        daily = live["daily"]
        for i, date_str in enumerate(daily.get("time", [])[:7]):
            d_tmax  = float(daily["temperature_2m_max"][i] or temp)
            d_rain  = float(daily["precipitation_sum"][i] or 0)
            d_wind  = float(daily["wind_speed_10m_max"][i] or wind)
            d_rh    = max(15, rh + (temp - d_tmax) * 2)
            d_ffmc  = _fwi_ffmc(d_tmax, d_rh, d_wind, d_rain)
            d_dmc   = _fwi_dmc(d_tmax, d_rh, d_rain, month)
            d_isi   = _fwi_isi(d_ffmc, d_wind)
            d_bui   = _fwi_bui(d_dmc)
            d_fwi   = _fwi_final(d_isi, d_bui)
            if month in [3,4,5]:       d_fwi = min(d_fwi*1.35, 120)
            elif month in [6,7,8,9]:   d_fwi = d_fwi*0.45
            d_danger, _ = _danger_class(d_fwi)
            forecast_7d.append({
                "date":    date_str,
                "fwi":     round(d_fwi, 1),
                "danger":  d_danger,
                "tmax":    round(d_tmax, 1),
                "rain_mm": round(d_rain, 1),
                "wind":    round(d_wind, 1),
                "rh":      round(d_rh, 1),
            })

    # ── Factor breakdown ──────────────────────────────────────
    t_norm = max(temp - 10, 0) / 35
    h_norm = max(1 - rh/100, 0)
    w_norm = min(wind / 50, 1)
    r_norm = max(1 - rain/20, 0)
    total  = t_norm + h_norm + w_norm + r_norm + 0.001
    factors = {
        "Temperature":   round(t_norm/total*100, 1),
        "Low humidity":  round(h_norm/total*100, 1),
        "Wind speed":    round(w_norm/total*100, 1),
        "Dry conditions":round(r_norm/total*100, 1),
    }

    return {
        "location":      location_name,
        "fwi":           round(fwi, 1),
        "danger":        danger,
        "danger_color":  d_color,
        "temperature":   round(temp, 1),
        "humidity":      round(rh, 1),
        "wind_kmh":      round(wind, 1),
        "rain_mm":       round(rain, 1),
        "ffmc":          ffmc,
        "dmc":           dmc,
        "isi":           isi,
        "bui":           bui,
        "fire_count_250km": fire_count,
        "fires_nearby":  fire_rows,
        "dust_ug_m3":    dust,
        "pm10_ug_m3":    pm10,
        "factors":       factors,
        "forecast_7d":   forecast_7d,
        "firms_enabled": bool(fire_rows or fire_count == 0),
        "data_sources": [
            "Open-Meteo Live (Canadian FWI inputs)",
            "NASA FIRMS VIIRS/MODIS (active fire detections)",
            "Open-Meteo Air Quality (smoke/dust)",
        ],
    }
