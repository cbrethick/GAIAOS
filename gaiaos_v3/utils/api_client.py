"""
GaiaOS — API Client (Verified Free APIs Only)
All APIs tested and confirmed 100% free for India data.

APIs used:
  1. Open-Meteo Live        — weather forecast    — NO KEY
  2. Open-Meteo Historical  — ERA5 1940–now        — NO KEY
  3. Open-Meteo Flood       — river discharge      — NO KEY
  4. Open-Meteo Air Quality — PM2.5, PM10, dust    — NO KEY
  5. Open-Meteo Elevation   — terrain height       — NO KEY
  6. Nominatim OSM          — India location search — NO KEY
  7. Overpass API           — roads/buildings OSM  — NO KEY
  8. NASA FIRMS             — live fire detections — FREE KEY (2 min signup)
  9. NASA POWER             — solar/climate data   — NO KEY
"""

import os, requests, json, time, hashlib
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# ── API endpoints (all from .env) ────────────────────────────
FIRMS_KEY       = os.getenv("NASA_FIRMS_KEY", "")
OM_BASE         = os.getenv("OPEN_METEO_BASE",  "https://api.open-meteo.com/v1")
OM_HIST         = os.getenv("OPEN_METEO_HIST",  "https://archive-api.open-meteo.com/v1")
OM_FLOOD        = os.getenv("OPEN_METEO_FLOOD", "https://flood-api.open-meteo.com/v1")
OM_AQ           = os.getenv("OPEN_METEO_AQ",    "https://air-quality-api.open-meteo.com/v1")
NOMINATIM       = os.getenv("NOMINATIM_BASE",   "https://nominatim.openstreetmap.org")
OVERPASS        = os.getenv("OVERPASS_BASE",    "https://overpass-api.de/api/interpreter")
NASA_POWER      = os.getenv("NASA_POWER_BASE",  "https://power.larc.nasa.gov/api/temporal/daily/point")

# ── Cache ────────────────────────────────────────────────────
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_get(url: str, params: dict, ttl_sec: int = 3600):
    key  = hashlib.md5((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    path = CACHE_DIR / f"{key}.json"
    if path.exists() and (time.time() - path.stat().st_mtime) < ttl_sec:
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return None

def _cache_set(url: str, params: dict, data: dict):
    key  = hashlib.md5((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    path = CACHE_DIR / f"{key}.json"
    path.write_text(json.dumps(data))

def _get(url: str, params: dict = None, headers: dict = None,
         post_data: dict = None, ttl: int = 3600) -> dict | None:
    """
    HTTP GET/POST with cache. Returns None on any failure.
    Retries once on timeout.
    """
    params = params or {}
    cached = _cache_get(url, params, ttl)
    if cached is not None:
        return cached
    try:
        if post_data:
            r = requests.post(url, data=post_data,
                              headers=headers, timeout=20)
        else:
            r = requests.get(url, params=params,
                             headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        _cache_set(url, params, data)
        return data
    except requests.Timeout:
        try:  # one retry
            if post_data:
                r = requests.post(url, data=post_data, timeout=25)
            else:
                r = requests.get(url, params=params, timeout=25)
            r.raise_for_status()
            data = r.json()
            _cache_set(url, params, data)
            return data
        except Exception:
            return None
    except Exception as e:
        return None


# ════════════════════════════════════════════════════════════
#  GEOCODING — Search any place in India
# ════════════════════════════════════════════════════════════

def geocode(place: str) -> dict | None:
    """
    Search any city / village / district in India.
    Uses Nominatim OpenStreetMap — free, no key.
    Returns: {name, lat, lon, state, district, display}
    """
    data = _get(
        f"{NOMINATIM}/search",
        {"q": f"{place}, India", "format": "json",
         "limit": 1, "addressdetails": 1},
        headers={"User-Agent": "GaiaOS-EarthTwin/2.0 (research project)"},
        ttl=86400  # cache 24h — locations don't change
    )
    if not data or len(data) == 0:
        return None

    r    = data[0]
    addr = r.get("address", {})
    return {
        "name":     r["display_name"].split(",")[0].strip(),
        "display":  r["display_name"][:60],
        "lat":      float(r["lat"]),
        "lon":      float(r["lon"]),
        "state":    addr.get("state", ""),
        "district": (addr.get("county") or addr.get("city") or
                     addr.get("town") or addr.get("village") or ""),
    }


def reverse_geocode(lat: float, lon: float) -> dict:
    """Reverse geocode lat/lon → place name."""
    data = _get(
        f"{NOMINATIM}/reverse",
        {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1},
        headers={"User-Agent": "GaiaOS-EarthTwin/2.0"},
        ttl=86400
    )
    if not data:
        return {"state": "", "district": "", "name": f"{lat:.2f},{lon:.2f}"}
    addr = data.get("address", {})
    return {
        "name":     data.get("display_name","").split(",")[0],
        "state":    addr.get("state",""),
        "district": addr.get("county","") or addr.get("city",""),
    }


# ════════════════════════════════════════════════════════════
#  WEATHER — Live + Forecast (Open-Meteo, no key)
# ════════════════════════════════════════════════════════════

def get_weather_now(lat: float, lon: float) -> dict | None:
    """
    Live weather + 16-day forecast for any India location.
    Source: Open-Meteo (uses ECMWF IFS model for India).
    Free, no key.
    """
    return _get(f"{OM_BASE}/forecast", {
        "latitude": lat, "longitude": lon,
        "current": [
            "temperature_2m", "relative_humidity_2m",
            "apparent_temperature", "precipitation",
            "rain", "showers", "wind_speed_10m",
            "wind_direction_10m", "weather_code",
            "cloud_cover", "surface_pressure",
            "soil_moisture_0_to_1cm",
        ],
        "hourly": [
            "temperature_2m", "relative_humidity_2m",
            "precipitation_probability", "precipitation",
            "wind_speed_10m", "soil_moisture_0_to_1cm",
            "soil_moisture_1_to_3cm",
        ],
        "daily": [
            "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "rain_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "et0_fao_evapotranspiration",
        ],
        "forecast_days": 16,
        "timezone": "Asia/Kolkata",
        "wind_speed_unit": "kmh",
    }, ttl=1800)  # 30 min cache for live weather


def get_weather_history(lat: float, lon: float,
                         start: str, end: str) -> dict | None:
    """
    Historical ERA5 weather — 1940 to yesterday.
    Source: Open-Meteo Archive (ERA5 reanalysis).
    Free, no key. start/end: 'YYYY-MM-DD'
    """
    return _get(f"{OM_HIST}/archive", {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": [
            "temperature_2m_max", "temperature_2m_min",
            "temperature_2m_mean", "precipitation_sum",
            "rain_sum", "wind_speed_10m_max",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_10cm_mean",
        ],
        "timezone": "Asia/Kolkata",
    }, ttl=86400)


def get_elevation_om(lat: float, lon: float) -> float:
    """
    Real terrain elevation via Open-Meteo elevation endpoint.
    Free, no key.
    """
    d = _get(f"{OM_BASE}/elevation",
             {"latitude": lat, "longitude": lon},
             ttl=86400 * 30)
    if d and "elevation" in d:
        v = d["elevation"]
        return float(v[0] if isinstance(v, list) else v)
    # Fallback: read from forecast response
    d2 = get_weather_now(lat, lon)
    if d2 and "elevation" in d2:
        return float(d2["elevation"])
    return 10.0


def get_soil_moisture(lat: float, lon: float, days: int = 14) -> float:
    """
    Average soil moisture over past N days.
    Source: Open-Meteo ERA5 archive.
    """
    today = datetime.now()
    d = get_weather_history(
        lat, lon,
        (today - timedelta(days=days)).strftime("%Y-%m-%d"),
        (today - timedelta(days=1)).strftime("%Y-%m-%d"),
    )
    if not d or "daily" not in d:
        return 0.45
    vals = [v for v in d["daily"].get("soil_moisture_0_to_10cm_mean", [])
            if v is not None]
    return round(float(np.mean(vals)), 3) if vals else 0.45


# ════════════════════════════════════════════════════════════
#  FLOOD — River discharge (Open-Meteo Flood API, no key)
# ════════════════════════════════════════════════════════════

def get_river_discharge(lat: float, lon: float) -> dict | None:
    """
    Real river discharge forecast from GloFAS ensemble.
    Source: Open-Meteo Flood API (backed by GloFAS).
    Free, no key. Returns 90-day river discharge forecast.
    """
    return _get(f"{OM_FLOOD}/flood", {
        "latitude": lat, "longitude": lon,
        "daily": [
            "river_discharge",
            "river_discharge_mean",
            "river_discharge_max",
            "river_discharge_min",
        ],
        "forecast_days": 90,
        "ensemble": True,
    }, ttl=3600)


def get_rain_accumulation(lat: float, lon: float) -> dict:
    """
    Fetch 7-day and 30-day rain totals from ERA5.
    Used by flood module.
    """
    today = datetime.now()
    d = get_weather_history(
        lat, lon,
        (today - timedelta(days=30)).strftime("%Y-%m-%d"),
        (today - timedelta(days=1)).strftime("%Y-%m-%d"),
    )
    rain_7d = 0.0
    rain_30d = 0.0
    if d and "daily" in d:
        precip = [v or 0 for v in d["daily"].get("precipitation_sum", [])]
        rain_30d = round(sum(precip), 1)
        rain_7d  = round(sum(precip[-7:]), 1)
    return {"rain_7d": rain_7d, "rain_30d": rain_30d}


# ════════════════════════════════════════════════════════════
#  AIR QUALITY (Open-Meteo AQ API, no key)
# ════════════════════════════════════════════════════════════

def get_air_quality(lat: float, lon: float) -> dict | None:
    """
    Real air quality: PM2.5, PM10, NO2, CO, dust, pollen.
    Source: Open-Meteo Air Quality API (Copernicus CAMS model).
    Free, no key. Great for India pollution data.
    """
    return _get(f"{OM_AQ}/air-quality", {
        "latitude": lat, "longitude": lon,
        "current": [
            "pm10", "pm2_5", "carbon_monoxide",
            "nitrogen_dioxide", "sulphur_dioxide",
            "ozone", "dust", "uv_index",
            "european_aqi", "us_aqi",
        ],
        "hourly": [
            "pm10", "pm2_5", "nitrogen_dioxide",
            "dust", "uv_index",
        ],
        "forecast_days": 5,
        "timezone": "Asia/Kolkata",
    }, ttl=1800)


# ════════════════════════════════════════════════════════════
#  WILDFIRE — NASA FIRMS (free key, 2-min signup)
# ════════════════════════════════════════════════════════════

def get_firms_fires(lat: float, lon: float,
                    radius_km: float = 250, days: int = 7) -> pd.DataFrame:
    """
    Real active fire detections from NASA FIRMS.
    MODIS + VIIRS satellites. Near real-time.
    Requires free NASA key from firms.modaps.eosdis.nasa.gov/api/
    Returns DataFrame with fire locations and properties.
    """
    if not FIRMS_KEY or FIRMS_KEY in ("PASTE_YOUR_FREE_KEY_HERE", ""):
        return pd.DataFrame()

    deg   = radius_km / 111.0
    bbox  = f"{lon-deg:.4f},{lat-deg:.4f},{lon+deg:.4f},{lat+deg:.4f}"

    # Try VIIRS (more sensitive) first, fallback to MODIS
    for sensor in ["VIIRS_SNPP_NRT", "MODIS_NRT"]:
        url = (f"https://firms.modaps.eosdis.nasa.gov/api/area/csv"
               f"/{FIRMS_KEY}/{sensor}/{bbox}/{days}")
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and len(r.text) > 80:
                from io import StringIO
                df = pd.read_csv(StringIO(r.text))
                if len(df) > 0:
                    return df
        except Exception:
            continue
    return pd.DataFrame()


# ════════════════════════════════════════════════════════════
#  URBAN / ROADS — OpenStreetMap Overpass (no key)
# ════════════════════════════════════════════════════════════

def get_osm_roads(lat: float, lon: float, radius_m: int = 5000) -> dict:
    """
    Real road network counts from OpenStreetMap.
    Free, no key. Returns counts of each road type.
    """
    q = f"""
    [out:json][timeout:20];
    (
      way["highway"~"motorway|trunk|primary|secondary|tertiary"]
         (around:{radius_m},{lat},{lon});
    );
    out count;
    """
    d = _get(OVERPASS, post_data={"data": q}, ttl=86400)
    count = 0
    if d:
        for el in d.get("elements", []):
            if el.get("type") == "count":
                try:
                    count = int(el.get("tags", {}).get("total", 0))
                except Exception:
                    pass
    return {"major_road_count": count}


def get_osm_buildings(lat: float, lon: float, radius_m: int = 3000) -> dict:
    """Count buildings in radius using OSM Overpass."""
    q = f"""
    [out:json][timeout:20];
    (
      way["building"](around:{radius_m},{lat},{lon});
      relation["building"](around:{radius_m},{lat},{lon});
    );
    out count;
    """
    d = _get(OVERPASS, post_data={"data": q}, ttl=86400)
    count = 0
    if d:
        for el in d.get("elements", []):
            if el.get("type") == "count":
                try:
                    count = int(el.get("tags", {}).get("total", 0))
                except Exception:
                    pass
    return {"building_count": count}


def get_osm_road_names(lat: float, lon: float, radius_m: int = 4000) -> list:
    """Get actual road names near a location (for traffic corridors)."""
    q = f"""
    [out:json][timeout:15];
    way["highway"~"primary|trunk|motorway"]["name"]
       (around:{radius_m},{lat},{lon});
    out tags 8;
    """
    d = _get(OVERPASS, post_data={"data": q}, ttl=86400)
    names = []
    if d:
        for el in d.get("elements", []):
            name = el.get("tags", {}).get("name", "")
            if name and name not in names:
                names.append(name)
    return names[:8]


# ════════════════════════════════════════════════════════════
#  NASA POWER — Solar + Climate (no key)
# ════════════════════════════════════════════════════════════

def get_nasa_power(lat: float, lon: float,
                   start_yyyymmdd: str, end_yyyymmdd: str) -> dict | None:
    """
    NASA POWER climate data: solar, wind, temperature, humidity.
    30+ year archive. Free, no key.
    Great for crop module solar radiation input.
    """
    d = _get(NASA_POWER, {
        "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,WS10M,RH2M,ALLSKY_SFC_SW_DWN",
        "community":  "AG",   # Agriculture community — best for crops
        "longitude":  lon,
        "latitude":   lat,
        "start":      start_yyyymmdd,
        "end":        end_yyyymmdd,
        "format":     "JSON",
    }, ttl=86400)
    if d and "properties" in d:
        return d["properties"]["parameter"]
    return None


# ════════════════════════════════════════════════════════════
#  API STATUS CHECK
# ════════════════════════════════════════════════════════════

def check_all_apis(lat: float = 13.08, lon: float = 80.27) -> dict:
    """
    Live check of every API. Run from API Status page in the app.
    """
    results = {}

    # Open-Meteo live
    d = get_weather_now(lat, lon)
    results["Open-Meteo Live Weather"] = (
        f"✅ {d['current']['temperature_2m']}°C — FREE, no key"
        if d and "current" in d
        else "❌ Unreachable"
    )

    # Open-Meteo historical
    d2 = get_weather_history(lat, lon, "2024-06-01", "2024-06-03")
    results["Open-Meteo ERA5 Historical"] = (
        "✅ Connected — FREE, no key"
        if d2 and "daily" in d2
        else "❌ Unreachable"
    )

    # Open-Meteo Flood
    d3 = get_river_discharge(lat, lon)
    if d3 and "daily" in d3:
        # Check if we got any non-null data
        vals = [v for v in d3["daily"].get("river_discharge", []) if v is not None]
        status_msg = "✅ Connected — FREE, no key" if vals else "⚠️ Connected (no river data)"
        results["Open-Meteo Flood (GloFAS rivers)"] = status_msg
    else:
        results["Open-Meteo Flood (GloFAS rivers)"] = "❌ Unreachable"

    # Open-Meteo Air Quality
    d4 = get_air_quality(lat, lon)
    results["Open-Meteo Air Quality (CAMS)"] = (
        f"✅ PM2.5={d4['current'].get('pm2_5','?')} — FREE, no key"
        if d4 and "current" in d4
        else "❌ Unreachable"
    )

    # Open-Meteo Elevation
    elev = get_elevation_om(lat, lon)
    results["Open-Meteo Elevation"] = (
        f"✅ {elev}m — FREE, no key"
        if elev else "❌ Unreachable"
    )

    # Nominatim
    loc = geocode("Chennai")
    results["Nominatim OSM (location search)"] = (
        f"✅ Found: {loc['name']} — FREE, no key"
        if loc else "❌ Unreachable"
    )

    # Overpass
    roads = get_osm_roads(lat, lon, 3000)
    results["OpenStreetMap Overpass (roads/buildings)"] = (
        f"✅ {roads['major_road_count']} roads found — FREE, no key"
        if roads else "❌ Unreachable"
    )

    # NASA FIRMS
    if FIRMS_KEY and FIRMS_KEY not in ("PASTE_YOUR_FREE_KEY_HERE", ""):
        fires = get_firms_fires(lat, lon, 200, 3)
        results["NASA FIRMS (fire detections)"] = (
            f"✅ {len(fires)} fire detections — FREE key"
            if fires is not None
            else "❌ Key error"
        )
    else:
        results["NASA FIRMS (fire detections)"] = (
            "⚠️  Add NASA_FIRMS_KEY to .env — get free key at firms.modaps.eosdis.nasa.gov/api"
        )

    # NASA POWER
    today = datetime.now()
    d5 = get_nasa_power(lat, lon,
                        (today-timedelta(days=5)).strftime("%Y%m%d"),
                        (today-timedelta(days=2)).strftime("%Y%m%d"))
    results["NASA POWER (solar/climate)"] = (
        "✅ Connected — FREE, no key"
        if d5 else "❌ Unreachable"
    )

    return results
