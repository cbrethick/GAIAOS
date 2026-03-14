"""
GaiaOS — Earth Digital Twin AI  |  Real Data Edition
Run: streamlit run app.py
Search any location in India → get live predictions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from utils.api_client  import geocode, check_all_apis
from modules.flood     import predict_flood
from modules.climate   import predict_climate
from modules.crop      import predict_crop_yield, CROPS
from modules.wildfire  import predict_wildfire
from modules.traffic   import predict_traffic, predict_urban_growth

try:
    from streamlit_folium import st_folium
    import folium
    FOLIUM = True
except ImportError:
    FOLIUM = False

st.set_page_config(page_title="GaiaOS", page_icon="🌍",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
.stApp{background:#080c0f}
section[data-testid="stSidebar"]{background:#0d1318;border-right:1px solid #1e2d3d}
.block-container{padding-top:1rem}
div[data-testid="metric-container"]{background:#111920;border:1px solid #1e2d3d;border-radius:8px;padding:12px}
div[data-testid="metric-container"] label{color:#7a8fa0!important;font-size:12px}
.src{font-size:11px;color:#3d5060;font-family:monospace;margin-top:8px;padding:6px 8px;background:#0d1318;border-radius:4px}
#MainMenu,footer,header{visibility:hidden}
</style>""", unsafe_allow_html=True)

BG="#080c0f"; GR="#1e2d3d"; TX="#e8edf2"

def dfig(fig, h=300):
    fig.update_layout(height=h, paper_bgcolor=BG, plot_bgcolor=BG,
                      font=dict(color=TX,size=12),
                      margin=dict(l=8,r=8,t=30,b=8),
                      xaxis=dict(gridcolor=GR,color=TX),
                      yaxis=dict(gridcolor=GR,color=TX),
                      legend=dict(bgcolor=BG))
    return fig

def risk_color(level):
    return {"Low":"#22c55e","Moderate":"#eab308","High":"#f97316",
            "Very High":"#ef4444","Extreme":"#7f1d1d"}.get(level,"#fbbf24")

def make_map(lat, lon, score, label, module):
    if not FOLIUM:
        return None
    colors = {"flood":["#22c55e","#fbbf24","#f97316","#dc2626"],
              "climate":["#3b82f6","#93c5fd","#fbbf24","#dc2626"],
              "crop":["#dc2626","#fbbf24","#22c55e"],
              "wildfire":["#22c55e","#fbbf24","#f97316","#7f1d1d"],
              "traffic":["#22c55e","#fbbf24","#f97316","#dc2626"]}
    pal = colors.get(module, colors["flood"])
    col = pal[min(int(score/100*len(pal)), len(pal)-1)]
    m = folium.Map(location=[lat,lon], zoom_start=11,
                   tiles="CartoDB dark_matter", prefer_canvas=True)
    folium.CircleMarker([lat,lon], radius=20, color=col,
                        fill=True, fill_color=col, fill_opacity=0.6,
                        weight=2, tooltip=f"{label}: {score:.1f}").add_to(m)
    folium.CircleMarker([lat,lon], radius=38, color=col,
                        fill=False, weight=1, opacity=0.25).add_to(m)
    return m

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 GaiaOS")
    st.caption("Earth Digital Twin · Real Data")
    st.divider()

    MODULE = st.selectbox("Module", [
        "🏠 Home",
        "🌊 Flood Probability",
        "🌤 Climate Patterns",
        "🌾 Crop Yield",
        "🔥 Wildfire Risk",
        "🚗 Traffic & Urban Growth",
        "⚙️ API Status",
    ])
    st.divider()

    st.markdown("**🔍 Search any India location**")
    query  = st.text_input("City / district / village / pin",
                            placeholder="e.g. Wayanad Kerala")
    search = st.button("Search", use_container_width=True)

    if "loc" not in st.session_state:
        st.session_state.loc = None

    if search and query.strip():
        with st.spinner("Searching…"):
            loc = geocode(query.strip())
        if loc:
            st.session_state.loc = loc
            st.success(f"📍 {loc['name'][:35]}")
        else:
            st.error("Not found. Try adding state name.")

    if st.session_state.loc:
        L = st.session_state.loc
        st.markdown(f"""<div style='background:#0d1318;border:1px solid #1e2d3d;
        border-radius:6px;padding:8px;font-size:11px;color:#7a8fa0;font-family:monospace'>
        📍 {L.get('district','') or L['name'][:22]}<br>
        {L.get('state','')}<br>
        {L['lat']:.4f}°N · {L['lon']:.4f}°E
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("""<div style='font-size:11px;color:#3d5060;line-height:1.9'>
    <b style='color:#7a8fa0'>Free APIs used</b><br>
    Open-Meteo ERA5 (weather)<br>
    Open-Meteo Flood/GloFAS<br>
    Open-Meteo Air Quality<br>
    NASA FIRMS (fires, free key)<br>
    NASA POWER (solar/climate)<br>
    OpenStreetMap Overpass<br>
    Nominatim (location search)<br>
    <br><b style='color:#2d9cff'>All 100% free · No billing</b>
    </div>""", unsafe_allow_html=True)

def need_loc():
    if not st.session_state.get("loc"):
        st.info("👈 Type any city or village in the sidebar search box, then click Search.")
        st.stop()
    return st.session_state.loc

# ── HOME ──────────────────────────────────────────────────────
if "Home" in MODULE:
    st.markdown("# 🌍 GaiaOS — Earth Digital Twin AI")
    st.markdown("<p style='color:#7a8fa0'>Live predictions from real satellite + weather APIs for any location in India. 100% free.</p>", unsafe_allow_html=True)
    st.info("👈 Type any location in the sidebar search box → choose a module → get real predictions instantly.")

    cols = st.columns(5)
    for col, (icon, name, sub, c) in zip(cols, [
        ("🌊","Flood","72h risk","#2d9cff"),
        ("🌤","Climate","30-day","#a78bfa"),
        ("🌾","Crop","Harvest","#34d399"),
        ("🔥","Wildfire","FWI index","#fb923c"),
        ("🚗","Urban","City growth","#fbbf24")
    ]):
        with col:
            st.markdown(f"""<div style='background:#111920;border:1px solid {c}44;
            border-radius:8px;padding:14px;text-align:center'>
            <div style='font-size:24px'>{icon}</div>
            <div style='font-weight:700;font-size:13px;color:{c};margin:5px 0'>{name}</div>
            <div style='font-size:11px;color:#7a8fa0'>{sub}</div></div>""",
            unsafe_allow_html=True)

# ── FLOOD ──────────────────────────────────────────────────────
elif "Flood" in MODULE:
    L = need_loc()
    st.markdown(f"### 🌊 Flood Probability — {L.get('district','') or L['name'][:25]}, {L.get('state','')}")

    with st.spinner("Fetching ERA5 rainfall, GloFAS river data, soil moisture…"):
        R = predict_flood(L["lat"], L["lon"], L.get("name",""))

    if "error" in R:
        st.error(R["error"]); st.stop()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Flood Probability", f"{R['probability']}%")
    c2.metric("Risk Level", R["risk_level"])
    c3.metric("7-day Rainfall", f"{R['rain_7d_mm']} mm")
    c4.metric("Soil Moisture", f"{R['soil_moisture']:.2f}")

    rc = risk_color(R["risk_level"])
    st.markdown(f"""<div style='background:#111920;border:2px solid {rc};
    border-radius:8px;padding:14px;margin:10px 0;display:flex;gap:24px;align-items:center'>
    <div style='font-size:36px;font-weight:800;color:{rc}'>{R['probability']}%</div>
    <div>
      <div style='font-size:18px;font-weight:700;color:{rc}'>{R['risk_level']} Risk</div>
      <div style='font-size:12px;color:#7a8fa0'>Rain today: {R['rain_today_mm']}mm ·
      30-day: {R['rain_30d_mm']}mm · Elevation: {R['elevation_m']}m</div>
      {f"<div style='font-size:12px;color:#fbbf24'>River discharge: {R['river_discharge_m3s']:.1f} m³/s</div>"
       if R.get('river_discharge_m3s') else ""}
    </div></div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### Feature importance (model trained on 5yr ERA5)")
        for f, v in R["factors"].items():
            bc = "#2d9cff" if v < 25 else "#f97316" if v < 45 else "#dc2626"
            st.markdown(f"""<div style='display:flex;justify-content:space-between;font-size:13px;margin:3px 0'>
            <span>{f}</span><b>{v}%</b></div>
            <div style='height:4px;background:#1e2d3d;border-radius:2px;margin-bottom:3px'>
            <div style='height:100%;width:{v}%;background:{bc};border-radius:2px'></div></div>""",
            unsafe_allow_html=True)

    with col_r:
        st.markdown("#### 7-day rainfall + flood probability")
        if R["rain_forecast"]:
            fd = pd.DataFrame(R["rain_forecast"])
            fig = go.Figure()
            fig.add_bar(x=fd["date"], y=fd["rain_mm"], name="Rain mm",
                        marker_color="#3b82f6", yaxis="y1")
            fig.add_scatter(x=fd["date"], y=fd["flood_prob"], mode="lines+markers",
                            name="Flood %", line=dict(color="#dc2626",width=2),
                            marker=dict(size=6), yaxis="y2")
            fig.update_layout(yaxis=dict(title="Rain mm",gridcolor=GR,color=TX),
                              yaxis2=dict(title="Flood %",overlaying="y",side="right",
                                          range=[0,100],color="#dc2626"),
                              legend=dict(orientation="h",bgcolor=BG),
                              height=280, paper_bgcolor=BG, plot_bgcolor=BG,
                              font=dict(color=TX), margin=dict(l=8,r=8,t=10,b=8),
                              xaxis=dict(gridcolor=GR,color=TX))
            st.plotly_chart(fig, use_container_width=True)

    if R.get("river_7d_forecast"):
        st.markdown("#### GloFAS river discharge forecast (7 days)")
        rv = pd.DataFrame(R["river_7d_forecast"])
        fig2 = px.area(rv, x="date", y="discharge",
                       color_discrete_sequence=["#2d9cff"],
                       labels={"discharge":"m³/s"})
        st.plotly_chart(dfig(fig2, 220), use_container_width=True)

    if FOLIUM:
        m = make_map(L["lat"],L["lon"],R["probability"],"Flood risk","flood")
        st_folium(m, width=700, height=360, key="fmap")

    st.markdown(f"<div class='src'>Sources: {' · '.join(R['data_sources'])}</div>",
                unsafe_allow_html=True)

# ── CLIMATE ──────────────────────────────────────────────────
elif "Climate" in MODULE:
    L = need_loc()
    st.markdown(f"### 🌤 Climate Patterns — {L.get('district','') or L['name'][:25]}, {L.get('state','')}")

    with st.spinner("Computing ERA5 30-year normals + live 16-day forecast…"):
        R = predict_climate(L["lat"], L["lon"], L.get("state",""), L.get("name",""))

    if "error" in R:
        st.error(R["error"]); st.stop()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Current Temp", f"{R['current_temp']}°C")
    c2.metric("vs 10yr Normal", R["anomaly_label"])
    c3.metric("Monsoon", R["monsoon_status"])
    c4.metric("Drought SPI", f"{R['spi']} — {R['drought_label']}")

    if R["spi"] < -1.5:
        st.error(f"⚠️ Drought alert: SPI {R['spi']} — {R['drought_label']}")
    elif R["spi"] > 1.5:
        st.success(f"🌧 Above-normal rainfall: SPI {R['spi']} — {R['drought_label']}")

    if R.get("forecast_16d"):
        fd = pd.DataFrame(R["forecast_16d"])
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 16-day temperature forecast")
            fig = go.Figure()
            fig.add_scatter(x=fd["date"], y=fd["tmax"], name="Max",
                            line=dict(color="#fb923c",width=1.5))
            fig.add_scatter(x=fd["date"], y=fd["tmin"], name="Min",
                            fill="tonexty", line=dict(color="#3b82f6",width=1.5),
                            fillcolor="rgba(59,130,246,0.12)")
            fig.add_scatter(x=fd["date"], y=fd["tmean"], name="Mean",
                            line=dict(color="#a78bfa",width=2))
            fig.add_hline(y=R["normal_temp"], line_dash="dot",
                          line_color="#fbbf24", annotation_text="10yr normal")
            st.plotly_chart(dfig(fig, 290), use_container_width=True)

        with col_r:
            st.markdown("#### Temperature anomaly (°C vs 10yr normal)")
            fig2 = px.bar(fd, x="date", y="anomaly",
                          color="anomaly",
                          color_continuous_scale=["#3b82f6","white","#dc2626"],
                          labels={"anomaly":"°C"})
            fig2.update_coloraxes(showscale=False)
            fig2.add_hline(y=0, line_dash="dot", line_color="#7a8fa0")
            st.plotly_chart(dfig(fig2, 290), use_container_width=True)

        st.markdown("#### Rainfall forecast")
        fig3 = px.bar(fd, x="date", y="rain_mm",
                      color_discrete_sequence=["#3b82f6"],
                      labels={"rain_mm":"mm"})
        st.plotly_chart(dfig(fig3, 200), use_container_width=True)

    if R.get("air_quality"):
        st.markdown("#### Live air quality (Copernicus CAMS)")
        aq = R["air_quality"]
        aq_cols = st.columns(min(len(aq), 5))
        for col, (k, v) in zip(aq_cols, aq.items()):
            col.metric(k.upper().replace("_"," "), round(float(v),1) if isinstance(v,(int,float)) else v)

    st.markdown(f"<div class='src'>Sources: {' · '.join(R['data_sources'])}</div>",
                unsafe_allow_html=True)

# ── CROP ──────────────────────────────────────────────────────
elif "Crop" in MODULE:
    L = need_loc()
    st.markdown(f"### 🌾 Crop Yield — {L.get('district','') or L['name'][:25]}, {L.get('state','')}")

    crop = st.selectbox("Crop", CROPS)

    with st.spinner(f"Fetching ERA5 growing season + NASA POWER solar data…"):
        R = predict_crop_yield(L["lat"], L["lon"], crop, L.get("name",""))

    if "error" in R:
        st.error(R["error"]); st.stop()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Predicted Yield", f"{R['predicted_yield']:,} kg/ha")
    pct = R["vs_national_avg"]
    c2.metric("vs National Average", f"{pct:+.1f}%",
              delta_color="normal" if pct>=0 else "inverse")
    c3.metric("Season Rainfall", f"{R['total_rain']} mm")
    c4.metric("Avg Temperature", f"{R['avg_temp']}°C")

    flag = R["food_flag"]
    if "ALERT" in flag:
        st.error(f"🚨 {flag}")
    elif "Warning" in flag:
        st.warning(f"⚠️ {flag}")
    else:
        st.success(f"✅ {flag}")

    st.caption(f"Season: {R['season']} · {R['growing_weeks']} weeks · Soil moisture: {R['avg_soil']:.3f}")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### NDVI proxy (water balance from ERA5 + ET0)")
        if R.get("ndvi_proxy"):
            nd = pd.DataFrame({"Week": range(1,len(R["ndvi_proxy"])+1),
                                "NDVI": R["ndvi_proxy"]})
            fig = px.area(nd, x="Week", y="NDVI",
                          color_discrete_sequence=["#34d399"])
            fig.update_yaxes(range=[0,1])
            st.plotly_chart(dfig(fig,270), use_container_width=True)

    with col_r:
        st.markdown("#### Yield vs 5-year history")
        if R.get("historical"):
            hd = pd.DataFrame(R["historical"])
            hd["clr"] = ["#34d399" if y==datetime.now().year else "#3d5060"
                          for y in hd["year"]]
            fig2 = px.bar(hd, x="year", y="yield",
                          color="clr", color_discrete_map="identity",
                          labels={"yield":"kg/ha"})
            fig2.update_layout(showlegend=False)
            st.plotly_chart(dfig(fig2,270), use_container_width=True)

    if R.get("stress_weekly"):
        st.markdown("#### Weekly crop health score (0=stressed, 1=optimal)")
        sd = pd.DataFrame({"Week": range(1,len(R["stress_weekly"])+1),
                            "Score": R["stress_weekly"]})
        fig3 = px.line(sd, x="Week", y="Score",
                       color_discrete_sequence=["#fbbf24"])
        fig3.update_yaxes(range=[0,1.1])
        fig3.add_hline(y=0.75, line_dash="dot", line_color="#22c55e",
                       annotation_text="Good threshold")
        st.plotly_chart(dfig(fig3, 200), use_container_width=True)

    st.markdown(f"<div class='src'>Sources: {' · '.join(R['data_sources'])}</div>",
                unsafe_allow_html=True)

# ── WILDFIRE ──────────────────────────────────────────────────
elif "Wildfire" in MODULE:
    L = need_loc()
    st.markdown(f"### 🔥 Wildfire Risk — {L.get('district','') or L['name'][:25]}, {L.get('state','')}")

    with st.spinner("Computing Canadian FWI + checking NASA FIRMS fires…"):
        R = predict_wildfire(L["lat"], L["lon"], L.get("name",""))

    if "error" in R:
        st.error(R["error"]); st.stop()

    dc = R["danger_color"]
    st.markdown(f"""<div style='background:#111920;border:2px solid {dc};
    border-radius:10px;padding:18px;text-align:center;margin:10px 0'>
    <div style='font-size:46px;font-weight:800;color:{dc}'>{R['fwi']}</div>
    <div style='font-size:16px;color:{dc};font-weight:700'>Fire Weather Index</div>
    <div style='font-size:22px;font-weight:700;margin-top:6px'>{R['danger']}</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Temperature", f"{R['temperature']}°C")
    c2.metric("Humidity",    f"{R['humidity']}%")
    c3.metric("Wind",        f"{R['wind_kmh']} km/h")
    c4.metric("Rain today",  f"{R['rain_mm']} mm")
    c5.metric("Fires (250km)", R["fire_count_250km"])

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### FWI components")
        for label, val in [("FFMC (fuel moisture)",R["ffmc"]),
                           ("DMC (duff moisture)", R["dmc"]),
                           ("ISI (spread index)",  R["isi"]),
                           ("BUI (build-up index)",R["bui"])]:
            st.markdown(f"**{label}:** `{val}`")

        st.markdown("#### Risk drivers")
        for f, v in R["factors"].items():
            bc = "#fb923c" if v > 25 else "#fbbf24"
            st.markdown(f"""<div style='display:flex;justify-content:space-between;font-size:13px;margin:3px 0'>
            <span>{f}</span><b>{v}%</b></div>
            <div style='height:4px;background:#1e2d3d;border-radius:2px;margin-bottom:3px'>
            <div style='height:100%;width:{v}%;background:{bc};border-radius:2px'></div></div>""",
            unsafe_allow_html=True)

        if R.get("dust_ug_m3"):
            st.metric("Dust (µg/m³)", R["dust_ug_m3"])
        if R.get("pm10_ug_m3"):
            st.metric("PM10 (µg/m³)", R["pm10_ug_m3"])

        if R["fires_nearby"]:
            st.markdown("#### 🔴 Active fires (NASA FIRMS, 7 days)")
            fdf = pd.DataFrame(R["fires_nearby"])
            st.dataframe(fdf[["lat","lon","date","brightness","frp","confidence"]],
                         use_container_width=True, hide_index=True)

    with col_r:
        st.markdown("#### 7-day fire danger forecast")
        if R.get("forecast_7d"):
            fd = pd.DataFrame(R["forecast_7d"])
            DCOLS = {"Low":"#22c55e","Moderate":"#eab308","High":"#f97316",
                     "Very High":"#ef4444","Extreme":"#7f1d1d"}
            fd["color"] = fd["danger"].map(DCOLS)
            fig = go.Figure(go.Bar(x=fd["date"], y=fd["fwi"],
                                   marker_color=fd["color"].tolist(),
                                   text=fd["danger"], textposition="auto"))
            fig.update_yaxes(range=[0,max(fd["fwi"].max()+10, 30)], title="FWI")
            st.plotly_chart(dfig(fig, 290), use_container_width=True)

            fig2 = go.Figure()
            fig2.add_bar(x=fd["date"], y=fd["rain_mm"], name="Rain mm",
                         marker_color="#3b82f6")
            fig2.add_scatter(x=fd["date"], y=fd["tmax"], name="Tmax °C",
                             line=dict(color="#fb923c"), yaxis="y2",
                             mode="lines+markers")
            fig2.update_layout(yaxis=dict(title="Rain mm",gridcolor=GR,color=TX),
                               yaxis2=dict(title="Temp °C",overlaying="y",side="right",
                                           color="#fb923c"),
                               height=240, paper_bgcolor=BG, plot_bgcolor=BG,
                               font=dict(color=TX), margin=dict(l=8,r=8,t=8,b=8),
                               xaxis=dict(gridcolor=GR,color=TX),
                               legend=dict(bgcolor=BG))
            st.plotly_chart(fig2, use_container_width=True)

    if FOLIUM:
        m = make_map(L["lat"],L["lon"],min(R["fwi"],100),"FWI","wildfire")
        if R["fires_nearby"]:
            for f in R["fires_nearby"]:
                folium.CircleMarker([f["lat"],f["lon"]], radius=5,
                                    color="#ff4400", fill=True,
                                    fill_color="#ff4400", fill_opacity=0.85,
                                    tooltip=f"Fire {f['date']} FRP:{f['frp']}").add_to(m)
        st_folium(m, width=700, height=360, key="wmap")

    st.markdown(f"<div class='src'>Sources: {' · '.join(R['data_sources'])}</div>",
                unsafe_allow_html=True)

# ── TRAFFIC & URBAN ──────────────────────────────────────────
elif "Traffic" in MODULE:
    L = need_loc()
    st.markdown(f"### 🚗 Traffic & Urban Growth — {L.get('district','') or L['name'][:25]}, {L.get('state','')}")

    tab1, tab2 = st.tabs(["🚦 Traffic Congestion", "🏙 Urban Growth"])

    with tab1:
        c1,c2 = st.columns(2)
        with c1: hour = st.slider("Hour", 0, 23, datetime.now().hour)
        with c2: day  = st.selectbox("Day type", ["Weekday","Weekend"])

        with st.spinner("Counting real roads + buildings from OpenStreetMap…"):
            R = predict_traffic(L["lat"],L["lon"],
                                L.get("district","") or L.get("name",""),
                                hour, day)

        cc = R["congestion_pct"]
        lc = {"Free flow":"#22c55e","Light":"#86efac","Moderate":"#fbbf24",
              "Heavy":"#f97316","Severe":"#dc2626"}.get(R["level"],"#fbbf24")
        st.markdown(f"""<div style='background:#111920;border:2px solid {lc};
        border-radius:10px;padding:16px;text-align:center;margin:10px 0'>
        <div style='font-size:40px;font-weight:800;color:{lc}'>{cc}%</div>
        <div style='font-size:18px;color:{lc}'>{R['level']} · {hour:02d}:00</div>
        <div style='font-size:12px;color:#7a8fa0;margin-top:4px'>{R['weather_impact']}</div>
        </div>""", unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        c1.metric("Urban density", f"{R['urban_score']:.1f}/100")
        c2.metric("Roads in 5km", R["road_count_5km"])
        c3.metric("Buildings in 3km", R["building_count_3km"])

        if R["road_corridors"]:
            st.markdown("#### Real road corridors (OpenStreetMap)")
            for road in R["road_corridors"]:
                st.markdown(f"🔴 `{road}`")

        if R.get("hourly_forecast"):
            hd = pd.DataFrame(R["hourly_forecast"])
            fig = px.area(hd, x="hour", y="congestion_pct",
                          color_discrete_sequence=["#fbbf24"],
                          labels={"congestion_pct":"Congestion %"})
            fig.add_vline(x=hour, line_color="#ff4444", line_dash="dot",
                          annotation_text=f"{hour:02d}:00")
            st.plotly_chart(dfig(fig, 260), use_container_width=True)

        st.markdown(f"<div class='src'>Sources: {' · '.join(R['data_sources'])}</div>",
                    unsafe_allow_html=True)

    with tab2:
        yrs = st.slider("Years ahead", 1, 10, 5)

        with st.spinner("Analysing OSM infrastructure density for growth model…"):
            R2 = predict_urban_growth(L["lat"],L["lon"],
                                      L.get("district","") or L.get("name",""), yrs)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Current urban %", f"{R2['current_urban_pct']}%")
        c2.metric(f"Predicted ({yrs}yr)", f"{R2['predicted_pct']}%",
                  f"+{R2['growth_pct']}%", delta_color="inverse")
        c3.metric("Farmland loss", f"{R2['farmland_loss_ha']:,} ha", delta_color="inverse")
        c4.metric("Expansion risk", R2["risk"])

        st.markdown(f"""Buildings in 5km: **{R2['buildings_5km']}** ·
        Roads in 8km: **{R2['roads_8km']}** ·
        Elevation: **{R2['elevation_m']}m** ·
        UHI temp trend: **{R2['uhi_temp_trend']:+.2f}°C/decade**""")

        if R2.get("yearly_forecast"):
            yd = pd.DataFrame(R2["yearly_forecast"])
            fig = go.Figure()
            fig.add_scatter(x=yd["year"], y=yd["urban_pct"],
                            mode="lines+markers", name="Predicted",
                            line=dict(color="#fbbf24",width=2),
                            marker=dict(size=8, color="#fbbf24"))
            fig.add_hline(y=R2["current_urban_pct"], line_dash="dot",
                          line_color="#3d5060", annotation_text="Today")
            fig.update_layout(yaxis_title="Urban area (%)",
                              xaxis_title="Year")
            st.plotly_chart(dfig(fig, 280), use_container_width=True)

        st.markdown(f"<div class='src'>Sources: {' · '.join(R2['data_sources'])}</div>",
                    unsafe_allow_html=True)

# ── API STATUS ────────────────────────────────────────────────
elif "API" in MODULE:
    st.markdown("# ⚙️ API Status")
    st.markdown("Live test of every data source.")

    with st.spinner("Testing all APIs…"):
        status = check_all_apis()

    for name, result in status.items():
        color = "#22c55e" if "✅" in result else "#f97316" if "⚠" in result else "#dc2626"
        st.markdown(f"""<div style='background:#111920;border:1px solid #1e2d3d;
        border-radius:8px;padding:11px 16px;margin:5px 0;display:flex;
        justify-content:space-between'>
        <span style='font-size:14px'>{name}</span>
        <span style='font-size:12px;color:{color};font-family:monospace'>{result}</span>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Your `.env` file — only one key needed")
    st.code("""# Copy .env.template → .env

# ONLY THIS ONE NEEDS REGISTRATION (free, 2 min):
NASA_FIRMS_KEY=get_from_firms.modaps.eosdis.nasa.gov/api

# Everything else is automatic — no keys needed:
# Open-Meteo weather, ERA5, Flood, Air Quality
# Nominatim OSM, Overpass API, NASA POWER, USGS elevation
""", language="bash")

# ── FOOTER ────────────────────────────────────────────────────
st.divider()
st.markdown("""<div style='text-align:center;color:#3d5060;font-size:11px;font-family:monospace;padding:6px'>
GaiaOS · Earth Digital Twin AI · Open-Meteo ERA5 · NASA FIRMS · OpenStreetMap · NASA POWER<br>
All APIs 100% free · No billing · Built for Google DeepMind · NVIDIA Earth-2 · Microsoft AI for Good · CERN
</div>""", unsafe_allow_html=True)
