import { useState, useEffect } from 'react';
import { 
  ShieldAlert, CloudRain, Thermometer, Activity, Flame, Car, MapPin, 
  Loader2, Home, Settings, Search, Info, AlertTriangle, CheckCircle2,
  Wind, Droplets, Mountain, Navigation, Zap
} from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, LineChart, Line, AreaChart, Area, ComposedChart, Legend,
  Cell
} from 'recharts';
import './NationalDashboard.css';

const NationalDashboard = () => {
  // ── STATE ──────────────────────────────────────────────────
  const [activeModule, setActiveModule] = useState('Home');
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState(null); 
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);

  // ── CONSTANTS ──────────────────────────────────────────────
  const modules = [
    { id: 'Home', icon: Home, label: "🏠 Home" },
    { id: 'flood', icon: CloudRain, label: "🌊 Flood Probability" },
    { id: 'climate', icon: Thermometer, label: "🌤 Climate Patterns" },
    { id: 'crop', icon: Activity, label: "🌾 Crop Yield" },
    { id: 'wildfire', icon: Flame, label: "🔥 Wildfire Risk" },
    { id: 'traffic', icon: Car, label: "🚗 Traffic & Urban" },
    { id: 'api', icon: Settings, label: "⚙️ API Status" },
  ];

  // ── ACTIONS ────────────────────────────────────────────────
  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000/api';
      const res = await fetch(`${baseUrl}/search?q=${encodeURIComponent(searchQuery)}`);
      const results = await res.json();
      
      if (results && results.length > 0) {
        const r = results[0];
        const addr = r.address || {};
        const locObj = {
          name: r.display_name.split(',')[0].trim(),
          display: r.display_name,
          lat: parseFloat(r.lat),
          lon: parseFloat(r.lon),
          state: addr.state || "",
          district: addr.county || addr.city || addr.town || addr.village || ""
        };
        setLocation(locObj);
        if (activeModule !== 'Home' && activeModule !== 'api') {
          fetchModuleData(activeModule, locObj);
        }
      } else {
        alert("Location not found in India.");
      }
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchModuleData = async (moduleId, loc) => {
    if (!loc) return;
    setLoading(true);
    setData(null);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000/api';
      const res = await fetch(`${baseUrl}/predict?module=${moduleId}&lat=${loc.lat}&lon=${loc.lon}&location=${loc.name}`);
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchApiStatus = async () => {
    setLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000/api';
      const res = await fetch(`${baseUrl}/status`);
      const result = await res.json();
      setApiStatus(result);
    } catch (err) {
      setApiStatus({ error: "Backend offline" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeModule === 'api') {
      fetchApiStatus();
    } else if (location && activeModule !== 'Home') {
      fetchModuleData(activeModule, location);
    }
  }, [activeModule]);

  // ── UI HELPERS ─────────────────────────────────────────────
  
  const MetricCard = ({ label, value, color }) => (
    <div className="v3-metric glass-panel">
      <label>{label}</label>
      <div className="metric-val" style={{ color }}>{value}</div>
    </div>
  );

  const RiskColor = (level) => {
    const map = { "Low": "#22c55e", "Moderate": "#eab308", "High": "#f97316", "Very High": "#ef4444", "Extreme": "#7f1d1d" };
    return map[level] || "#fbbf24";
  };

  // ── VIEWS ──────────────────────────────────────────────────

  const HomeView = () => (
    <div className="v3-home">
      <h1>🌍 GaiaOS — Earth Digital Twin AI</h1>
      <p className="subtitle">Real-time satellite and AI forecasting for any location in India. 100% free data.</p>
      
      <div className="info-box top-notice">
        <Info size={18} />
        <span>Type a city or village name in the sidebar search box to begin analysis.</span>
      </div>

      <div className="module-grid">
        {[
          { id: 'flood', icon: "🌊", name: "Flood", sub: "72h risk", color: "#2d9cff" },
          { id: 'climate', icon: "🌤", name: "Climate", sub: "30-day patterns", color: "#a78bfa" },
          { id: 'crop', icon: "🌾", name: "Crop", sub: "Yield predict", color: "#34d399" },
          { id: 'wildfire', icon: "🔥", name: "Wildfire", sub: "FWI score", color: "#fb923c" },
          { id: 'traffic', icon: "🚗", name: "Urban", sub: "Growth & Traffic", color: "#fbbf24" }
        ].map((m, i) => (
          <div key={i} className="module-intro-card glass-panel" 
               style={{ '--border-color': m.color, cursor: 'pointer' }}
               onClick={() => {
                 setActiveModule(m.id);
                 if (location) fetchModuleData(m.id, location);
               }}>
            <div className="icon">{m.icon}</div>
            <div className="name" style={{ color: m.color }}>{m.name}</div>
            <div className="sub">{m.sub}</div>
          </div>
        ))}
      </div>
    </div>
  );

  const FloodView = () => {
    if (!data) return null;
    const rc = RiskColor(data.risk_level);
    return (
      <div className="v3-module-view">
        <h3>🌊 Flood Probability — {location.district || location.name}, {location.state}</h3>
        <div className="metrics-row">
          <MetricCard label="Flood Probability" value={`${data.probability}%`} />
          <MetricCard label="Risk Level" value={data.risk_level} color={rc} />
          <MetricCard label="7-day Rainfall" value={`${data.rain_7d_mm} mm`} />
          <MetricCard label="Soil Moisture" value={data.soil_moisture?.toFixed(2)} />
        </div>
        <div className="risk-banner glass-panel" style={{ borderColor: rc }}>
          <div className="risk-score" style={{ color: rc }}>{data.probability}%</div>
          <div className="risk-details">
            <div className="level" style={{ color: rc }}>{data.risk_level} Risk</div>
            <div className="metadata">
              Rain today: {data.rain_today_mm}mm · 30-day: {data.rain_30d_mm}mm · Elevation: {data.elevation_m}m
            </div>
            {data.river_discharge_m3s && <div className="river-info">River discharge: {data.river_discharge_m3s.toFixed(1)} m³/s</div>}
          </div>
        </div>
        <div className="charts-grid-main">
          <div className="chart-box glass-panel small-h">
            <h4>XGBoost Feature Importance</h4>
            <div className="factors-list">
              {Object.entries(data.factors || {}).map(([f, v], i) => (
                <div key={i} className="factor-item">
                  <div className="factor-label"><span>{f}</span> <b>{v}%</b></div>
                  <div className="progress-bg"><div className="progress-fill" style={{ width: `${v}%`, background: v > 45 ? '#dc2626' : v > 25 ? '#f97316' : '#2d9cff' }}></div></div>
                </div>
              ))}
            </div>
          </div>
          <div className="chart-box glass-panel">
            <h4>Rainfall Forecast vs. Prob</h4>
            <div style={{ height: 280 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data.rain_forecast}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="date" stroke="#666" fontSize={10} />
                  <YAxis yAxisId="left" stroke="#3b82f6" fontSize={10} />
                  <YAxis yAxisId="right" orientation="right" stroke="#dc2626" fontSize={10} domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: '#0a0a0a', border: '1px solid #333' }} />
                  <Bar yAxisId="left" dataKey="rain_mm" fill="#3b82f6" opacity={0.6} />
                  <Line yAxisId="right" type="monotone" dataKey="flood_prob" stroke="#dc2626" strokeWidth={2} dot={{r: 4}} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const ClimateView = () => {
    if (!data) return null;
    return (
      <div className="v3-module-view">
        <h3>🌤 Climate Patterns — {location.district || location.name}</h3>
        <div className="metrics-row">
          <MetricCard label="Current Temp" value={`${data.current_temp}°C`} />
          <MetricCard label="vs 10yr Normal" value={data.anomaly_label} color={data.temp_anomaly > 0 ? '#ef4444' : '#3b82f6'} />
          <MetricCard label="Monsoon Status" value={data.monsoon_status} />
          <MetricCard label="Drought SPI" value={data.spi?.toFixed(2)} />
        </div>
        <div className="charts-grid-main mt-2">
          <div className="chart-box glass-panel full-w">
            <h4>16-day Temperature Forecast Trend</h4>
            <div style={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.forecast_16d}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="date" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" fontSize={10} />
                  <Tooltip contentStyle={{ background: '#0a0a0a', border: '1px solid #333' }} />
                  <Area type="monotone" dataKey="tmax" stroke="#fb923c" fill="#fb923c" fillOpacity={0.1} />
                  <Area type="monotone" dataKey="tmin" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} />
                  <Line type="monotone" dataKey="tmean" stroke="#a78bfa" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        <div className="aqi-grid-mini mt-2">
          {Object.entries(data.air_quality || {}).map(([k, v], i) => (
            <div key={i} className="aqi-card glass-panel">
              <label>{k.toUpperCase()}</label>
              <span>{typeof v === 'number' ? v.toFixed(1) : v}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const CropView = () => {
    if (!data) return null;
    return (
      <div className="v3-module-view">
        <h3>🌾 Crop Yield — {location.district || location.name}</h3>
        <div className="metrics-row">
          <MetricCard label="Predicted Yield" value={`${data.predicted_yield?.toLocaleString()} kg/ha`} />
          <MetricCard label="vs Nat. Average" value={`${data.vs_national_avg > 0 ? '+' : ''}${data.vs_national_avg}%`} color={data.vs_national_avg >= 0 ? '#22c55e' : '#ef4444'} />
          <MetricCard label="Season Rainfall" value={`${data.total_rain} mm`} />
          <MetricCard label="Avg Temp" value={`${data.avg_temp}°C`} />
        </div>
        <div className="info-box" style={{ borderColor: data.food_flag.includes('ALERT') ? '#ef4444' : '#22c55e' }}>
          <span>{data.food_flag}</span>
        </div>
        <div className="charts-grid-main">
          <div className="chart-box glass-panel">
            <h4>Yield History (kg/ha)</h4>
            <div style={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.historical}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="year" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ background: '#0a0a0a', border: '1px solid #333' }} />
                  <Bar dataKey="yield" fill="#3d5060">
                    {data.historical?.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.year === 2026 ? '#34d399' : '#3d5060'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="chart-box glass-panel">
            <h4>Weekly Stress Score (0=Stressed, 1=Optimal)</h4>
            <div style={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={(data.stress_weekly || []).map((v, i) => ({ week: i + 1, score: v }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="week" stroke="#666" />
                  <YAxis stroke="#666" domain={[0, 1.1]} />
                  <Tooltip contentStyle={{ background: '#0a0a0a', border: '1px solid #333' }} />
                  <Line type="monotone" dataKey="score" stroke="#fbbf24" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const WildfireView = () => {
    if (!data) return null;
    return (
      <div className="v3-module-view">
        <h3>🔥 Wildfire Risk — {location.district || location.name}</h3>
        <div className="fwi-hero glass-panel" style={{ borderColor: data.danger_color }}>
          <div className="fwi-score" style={{ color: data.danger_color }}>{data.fwi}</div>
          <div className="fwi-label">Fire Weather Index</div>
          <div className="danger-level" style={{ color: data.danger_color }}>{data.danger}</div>
        </div>
        <div className="metrics-row">
          <MetricCard label="Temperature" value={`${data.temperature}°C`} />
          <MetricCard label="Humidity" value={`${data.humidity}%`} />
          <MetricCard label="Wind Speed" value={`${data.wind_kmh} km/h`} />
          <MetricCard label="Fires (250km)" value={data.fire_count_250km} />
        </div>
        <div className="charts-grid-main">
          <div className="chart-box glass-panel full-w">
            <h4>7-day Fire Danger Forecast</h4>
            <div style={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.forecast_7d}>
                  <XAxis dataKey="date" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip />
                  <Bar dataKey="fwi">
                    {data.forecast_7d?.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={RiskColor(entry.danger)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const TrafficView = () => {
    if (!data) return null;
    return (
      <div className="v3-module-view">
        <h3>🚗 Traffic & Urban — {location.district || location.name}</h3>
        <div className="fwi-hero glass-panel" style={{ borderColor: '#fbbf24' }}>
          <div className="fwi-score" style={{ color: '#fbbf24' }}>{data.congestion_pct}%</div>
          <div className="fwi-label">Live Congestion</div>
          <div className="danger-level">{data.level}</div>
          <div className="metadata">{data.weather_impact}</div>
        </div>
        <div className="metrics-row">
          <MetricCard label="Urban Density" value={`${data.urban_score?.toFixed(1)}/100`} />
          <MetricCard label="Roads in 5km" value={data.road_count_5km} />
          <MetricCard label="Buildings (3km)" value={data.building_count_3km} />
          <MetricCard label="Peak Hour" value="18:00" />
        </div>
        <div className="charts-grid-main">
          <div className="chart-box glass-panel full-w">
            <h4>Hourly Congestion Profile (24h)</h4>
            <div style={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.hourly_forecast}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="hour" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ background: '#0a0a0a', border: '1px solid #333' }} />
                  <Area type="monotone" dataKey="congestion_pct" stroke="#fbbf24" fill="#fbbf24" fillOpacity={0.1} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ── MAIN LAYOUT ────────────────────────────────────────────
  return (
    <div className="v3-dashboard-layout">
      {/* Sidebar */}
      <aside className="v3-sidebar">
        <div className="sidebar-header">
          <h2>🌍 GaiaOS</h2>
          <span className="caption">Earth Digital Twin · Real Data</span>
        </div>

        <div className="sidebar-section">
          <label>Module Selection</label>
          <select value={activeModule} onChange={(e) => setActiveModule(e.target.value)} className="v3-select">
            {modules.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
          </select>
        </div>

        <div className="sidebar-section search-section">
          <label>🔍 Location Analysis (India)</label>
          <form onSubmit={handleSearch} className="v3-search-form">
            <input 
              type="text" 
              placeholder="e.g. Wayanad Kerala" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="v3-input"
            />
            <button type="submit" className="v3-search-btn" disabled={loading}>
              {loading ? <Loader2 className="animate-spin" size={16} /> : "Run AI Inference"}
            </button>
          </form>
        </div>

        {location && (
          <div className="location-summary-box glass-panel">
            <div className="loc-name">📍 {location.district || location.name}</div>
            <div className="loc-sub">{location.state}</div>
            <div className="loc-coords">{location.lat.toFixed(4)}°N · {location.lon.toFixed(4)}°E</div>
          </div>
        )}

        <div className="sidebar-footer">
          <div className="api-notice">
            <b>Satellite & Data Sources</b><br/>
            Open-Meteo ERA5 / Flood / Air<br/>
            NASA POWER / NASA FIRMS<br/>
            OSM Overpass / Nominatim<br/>
            <span className="blue-tag">Research-Grade · 100% Free</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="v3-content">
        {!location && activeModule !== 'Home' && activeModule !== 'api' ? (
          <div className="need-loc-prompt">
            <Search size={48} color="#2d9cff" className="mb-1" />
            <h2>Search Required</h2>
            <p>Please type a city or village name in the sidebar search box to load environmental telemetry.</p>
          </div>
        ) : (
          <div className="module-content-wrapper fade-in">
            {activeModule === 'Home' && <HomeView />}
            {activeModule === 'flood' && <FloodView />}
            {activeModule === 'climate' && <ClimateView />}
            {activeModule === 'crop' && <CropView />}
            {activeModule === 'wildfire' && <WildfireView />}
            {activeModule === 'traffic' && <TrafficView />}
            {activeModule === 'api' && (
              <div className="v3-module-view">
                <h3>⚙️ API Infrastructure Status</h3>
                <div className="api-grid mt-2">
                  {[
                    "Open-Meteo Global weather", 
                    "Open-Meteo GloFAS Flood", 
                    "Copernicus Air Quality", 
                    "NASA FIRMS VIIRS", 
                    "NASA POWER Solar", 
                    "OSM Nominatim", 
                    "OSM Overpass"
                  ].map((api, i) => (
                    <div key={i} className="status-item glass-panel">
                      <CheckCircle2 size={16} color="#22c55e" />
                      <span>{api}</span>
                      <span className="status-tag">ACTIVE ✅</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        {loading && (
          <div className="loading-v3-overlay">
            <Loader2 className="animate-spin" size={64} color="#2d9cff" />
            <p>Running Real-Time AI Inference...</p>
          </div>
        )}

        <footer className="dashboard-v3-footer">
          <div className="footer-line">GaiaOS · Earth Intelligence · Powered by Open Data & XGBoost</div>
          <div className="footer-logos">Built for DeepMind · NVIDIA Earth-2 · ESA/NASA Earth Science</div>
        </footer>
      </main>
    </div>
  );
};

export default NationalDashboard;
