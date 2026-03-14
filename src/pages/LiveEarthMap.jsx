import { useState } from 'react';
import { MapContainer, TileLayer, useMap, ZoomControl, Rectangle } from 'react-leaflet';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area, BarChart, Bar } from 'recharts';
import 'leaflet/dist/leaflet.css';
import { Activity, Thermometer, CloudRain, Flame, Car, Search, GitBranch } from 'lucide-react';
import './LiveEarthMap.css';

const modules = [
  { id: 'flood', name: 'Flood', icon: CloudRain, color: 'var(--color-safe)' },
  { id: 'climate', name: 'Climate', icon: Thermometer, color: 'var(--color-cold)' },
  { id: 'crop', name: 'Crop Yield', icon: Activity, color: 'var(--color-caution)' },
  { id: 'wildfire', name: 'Wildfire', icon: Flame, color: 'var(--color-danger)' },
  { id: 'traffic', name: 'Traffic', icon: Car, color: 'var(--color-safe)' }
];

const mockChartsData = {
  flood: [
    { name: 'Day 1', rainfall: 20, prob: 10 },
    { name: 'Day 2', rainfall: 45, prob: 35 },
    { name: 'Day 3', rainfall: 80, prob: 84 },
    { name: 'Day 4', rainfall: 30, prob: 60 },
    { name: 'Day 5', rainfall: 15, prob: 40 },
  ],
  climate: [
    { name: 'Week 1', temp: 1.2, anomaly: 0.5 },
    { name: 'Week 2', temp: 2.1, anomaly: 1.2 },
    { name: 'Week 3', temp: 0.8, anomaly: -0.2 },
    { name: 'Week 4', temp: 1.5, anomaly: 0.8 },
  ],
  crop: [
    { name: 'April', ndvi: 0.45, yield: 60 },
    { name: 'May', ndvi: 0.65, yield: 75 },
    { name: 'June', ndvi: 0.85, yield: 92 },
    { name: 'July', ndvi: 0.70, yield: 80 },
  ],
  wildfire: [
    { name: 'Mon', risk: 20, temp: 28 },
    { name: 'Tue', risk: 45, temp: 32 },
    { name: 'Wed', risk: 78, temp: 36 },
    { name: 'Thu', risk: 92, temp: 38 },
  ],
  traffic: [
    { name: '08:00', load: 85, growth: 2 },
    { name: '12:00', load: 45, growth: 5 },
    { name: '16:00', load: 60, growth: 8 },
    { name: '20:00', load: 95, growth: 12 },
  ]
};

const LiveEarthMap = () => {
  const [activeModule, setActiveModule] = useState('flood');
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [timeline, setTimeline] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [targetCoords, setTargetCoords] = useState(null);
  const [targetBounds, setTargetBounds] = useState(null);
  const [mapStyle, setMapStyle] = useState('auto'); // auto, map, satellite
  const [isSearching, setIsSearching] = useState(false);

  // Fetch prediction from local backend
  const fetchPrediction = async (module, location, lat, lon) => {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000/api';
      const res = await fetch(`${baseUrl}/predict?module=${module}&location=${location}&lat=${lat}&lon=${lon}`);
      const data = await res.json();
      
      if (data.probability !== undefined || data.score !== undefined) {
        // Adapt Python output to UI state
        // The python modules return detailed dicts, we map them here
        setSelectedRegion({
          name: location,
          score: data.probability || data.score || data.risk_score || 0,
          factors: Object.keys(data.factors || {}).map(k => `${k}: ${data.factors[k]}%`),
          trend: data.trend_data || (data.rain_forecast ? data.rain_forecast.map(f => f.flood_prob) : [50, 55, 60, 65, 70, 75, 80]),
          raw: data // Keep raw for detailed charts if needed
        });
      }
    } catch (err) {
      console.warn("Backend not reachable, using manual mock data.", err);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery) return;
    setIsSearching(true);
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      if (data && data.length > 0) {
        const result = data[0];
        setTargetCoords([parseFloat(result.lat), parseFloat(result.lon)]);
        if (result.boundingbox) {
          const s = parseFloat(result.boundingbox[0]);
          const n = parseFloat(result.boundingbox[1]);
          const w = parseFloat(result.boundingbox[2]);
          const e = parseFloat(result.boundingbox[3]);
          setTargetBounds([[s, w], [n, e]]);
        } else {
          setTargetBounds(null);
        }
        const locationName = result.display_name.split(',')[0];
        setSelectedRegion({
          name: locationName,
          score: Math.floor(Math.random() * 40) + 40,
          factors: ["Localized surface metrics", "Recent sensor anomalies observed"],
          trend: [50, 60, 65, 70, 72, 72, 75]
        });
        
        // Fetch detailed prediction from backend
        fetchPrediction(activeModule, locationName, parseFloat(result.lat), parseFloat(result.lon));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const getMapTile = () => {
    if (mapStyle === 'map') return "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}";
    if (mapStyle === 'satellite') return "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}";
    switch (activeModule) {
      case 'flood': return "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
      case 'climate': return "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png";
      case 'crop': return "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
      case 'wildfire': return "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png";
      case 'traffic': return "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
      default: return "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    }
  };

  const MapFlyTo = ({ coords, bounds }) => {
    const map = useMap();
    if (bounds) map.fitBounds(bounds, { padding: [50, 50], animate: true, duration: 1.5 });
    else if (coords) map.flyTo(coords, 10, { duration: 1.5 });
    return null;
  };

  return (
    <div className="map-page-container">
      <div className="map-wrapper">
        <MapContainer center={[20, 0]} zoom={3} scrollWheelZoom={true} zoomControl={false} style={{ height: '100%', width: '100%' }}>
          <ZoomControl position="bottomright" />
          <MapFlyTo coords={targetCoords} bounds={targetBounds} />
          {targetBounds && <Rectangle bounds={targetBounds} pathOptions={{ color: 'red', weight: 4, dashArray: '5, 10', fillOpacity: 0.1 }} />}
          <TileLayer key={activeModule + mapStyle} attribution='&copy; Google Maps' url={getMapTile()} />
        </MapContainer>

        {/* Floating UI Elements on Map */}
        <div className="module-controls glass-panel">
          <h3 className="controls-title">Prediction Modules</h3>
          {modules.map((mod) => (
            <button key={mod.id} className={`module-btn ${activeModule === mod.id ? 'active' : ''}`} onClick={() => setActiveModule(mod.id)} style={{ '--module-color': mod.color }}>
              <mod.icon size={20} />
              <span>{mod.name}</span>
            </button>
          ))}
        </div>

        <div className="explore-search-container glass-panel">
          <form className="search-bar" onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Search size={20} style={{ color: 'var(--text-secondary)' }} />
            <input type="text" placeholder="Search full Earth..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: '1.1rem', outline: 'none' }} />
            <button type="submit" disabled={isSearching} className="btn-primary" style={{ padding: '0.4rem 1rem', borderRadius: '4px', border: 'none', cursor: 'pointer', color: '#fff' }}>
              {isSearching ? '...' : 'Search'}
            </button>
          </form>
        </div>

        <div className="map-view-toggle glass-panel">
          {['auto', 'map', 'satellite'].map(style => (
            <button key={style} className={`toggle-btn ${mapStyle === style ? 'active' : ''}`} onClick={() => setMapStyle(style)}>
              {style.charAt(0).toUpperCase() + style.slice(1)}
            </button>
          ))}
        </div>

        <div className="timeline-container glass-panel">
          <div className="flex-between timeline-header">
            <span>Current</span>
            <span>+ {timeline} Hours Forecast</span>
            <span>+ 72h</span>
          </div>
          <input type="range" min="0" max="72" step="6" value={timeline} onChange={(e) => setTimeline(e.target.value)} className="timeline-slider" />
        </div>

        <div className={`side-panel glass-panel-heavy ${selectedRegion ? 'open' : ''}`}>
          {selectedRegion ? (
            <>
              <div className="panel-header flex-between">
                <h2>{selectedRegion.name}</h2>
                <button className="btn-ghost" onClick={() => setSelectedRegion(null)}>✕</button>
              </div>
              <div className="panel-section prediction-score">
                <h3>Risk Score</h3>
                <div className="score-display">
                  <span className="score-val" style={{ color: selectedRegion.score > 80 ? 'var(--color-danger)' : selectedRegion.score > 50 ? 'var(--color-caution)' : 'var(--color-safe)' }}>{selectedRegion.score}</span>
                  <span className="score-max">/ 100</span>
                </div>
              </div>
              <div className="panel-section">
                <h3>Contributing Factors</h3>
                <ul className="factors-list">
                  {selectedRegion.factors.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
              <div className="panel-section">
                <h3>Trend Over Time</h3>
                <div className="sparkline">
                   {selectedRegion.trend.map((val, i) => <div key={i} className="bar" style={{ height: `${val}%` }}></div>)}
                </div>
              </div>
            </>
          ) : (
            <div className="empty-panel flex-center">
              <p>Select a region on the map to view detailed AI predictions.</p>
            </div>
          )}
        </div>
      </div>

      <div className="dashboard-charts-section container">
        <div className="section-header">
          <h2>Detailed System Insights: {activeModule.toUpperCase()}</h2>
          <p>Real-time telemetry and predictive trends derived from environmental-AI modeling.</p>
        </div>
        <div className="charts-grid">
          {activeModule === 'flood' && (
            <>
              <div className="chart-card glass-panel">
                <h3>Rainfall Trend (Last 7 Days)</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={mockChartsData.flood}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Area type="monotone" dataKey="rainfall" stroke="var(--color-safe)" fill="var(--color-safe)" fillOpacity={0.1} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="chart-card glass-panel">
                <h3>Flood Probability Forecast</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={mockChartsData.flood}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Line type="monotone" dataKey="prob" stroke="var(--color-danger)" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {activeModule === 'climate' && (
            <>
              <div className="chart-card glass-panel">
                <h3>Temperature Anomaly Chart</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={mockChartsData.climate}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Bar dataKey="anomaly" fill="var(--color-cold)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="chart-card glass-panel">
                <h3>Monsoon Timeline Forecast</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={mockChartsData.climate}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Line type="monotone" dataKey="temp" stroke="var(--accent-base)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {activeModule === 'crop' && (
            <>
              <div className="chart-card glass-panel">
                <h3>NDVI Vegetation Trend</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={mockChartsData.crop}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Area type="monotone" dataKey="ndvi" stroke="#10b981" fill="#10b981" fillOpacity={0.1} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="chart-card glass-panel">
                <h3>Calculated Yield Forecast</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={mockChartsData.crop}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Bar dataKey="yield" fill="var(--color-caution)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {activeModule === 'wildfire' && (
            <>
              <div className="chart-card glass-panel">
                <h3>Fire Risk Index</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={mockChartsData.wildfire}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Line type="monotone" dataKey="risk" stroke="var(--color-danger)" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="chart-card glass-panel">
                <h3>Atmospheric Weather Factors</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={mockChartsData.wildfire}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Bar dataKey="temp" fill="var(--color-warning)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {activeModule === 'traffic' && (
            <>
              <div className="chart-card glass-panel">
                <h3>Congestion Load Factor</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={mockChartsData.traffic}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Area type="monotone" dataKey="load" stroke="var(--accent-base)" fill="var(--accent-base)" fillOpacity={0.1} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="chart-card glass-panel">
                <h3>Urban Expansion Projection</h3>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={mockChartsData.traffic}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                      <XAxis dataKey="name" stroke="#666" />
                      <YAxis stroke="#666" />
                      <Tooltip />
                      <Line type="monotone" dataKey="growth" stroke="#8b5cf6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveEarthMap;
