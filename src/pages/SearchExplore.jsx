import { useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Search, Map as MapIcon, Image as ImageIcon, Edit3, Trash2, Crosshair, BarChart2 } from 'lucide-react';
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './SearchExplore.css';

// Reusing same modules for tabs
const modules = ['Flood', 'Climate', 'Crop', 'Wildfire', 'Traffic'];
const mockChartData = [
  { time: 'Jan', val: 4000 },
  { time: 'Feb', val: 3000 },
  { time: 'Mar', val: 2000 },
  { time: 'Apr', val: 2780 },
  { time: 'May', val: 1890 },
  { time: 'Jun', val: 2390 },
  { time: 'Jul', val: 3490 },
];

const MapFlyTo = ({ coords }) => {
  const map = useMap();
  if (coords) {
    map.flyTo(coords, 10, { duration: 1.5 });
  }
  return null;
};

const SearchExplore = () => {
  const [mapType, setMapType] = useState('standard'); // standard | satellite
  const [searchQuery, setSearchQuery] = useState('');
  const [targetCoords, setTargetCoords] = useState(null);
  const [activeTab, setActiveTab] = useState('Flood');
  const [selectedRegion, setSelectedRegion] = useState(null); // Simulated selection

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery) return;
    // Mock geocoding
    const newCoords = [35.6895, 139.6917]; // always flies to Tokyo as mock
    setTargetCoords(newCoords);
    setSelectedRegion({
      name: searchQuery,
      score: 78,
      variables: ["Deforestation rate: +12%", "Precipitation: -4%"],
      indicators: "High anomaly in vegetation index"
    });
  };

  return (
    <div className="search-page-container">
      {/* Search Header */}
      <div className="search-header glass-panel">
        <form className="search-bar" onSubmit={handleSearch}>
          <Search size={20} className="search-icon" />
          <input 
            type="text" 
            placeholder="Search cities, districts, regions..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" style={{ padding: '0.5rem 1rem' }}>
            Analyze
          </button>
        </form>

        <div className="module-tabs">
          {modules.map(mod => (
            <button 
              key={mod} 
              className={`tab-btn ${activeTab === mod ? 'active' : ''}`}
              onClick={() => setActiveTab(mod)}
            >
              {mod}
            </button>
          ))}
        </div>
      </div>

      {/* Map Content */}
      <div className="search-map-wrapper">
        <MapContainer 
          center={[20, 0]} 
          zoom={3} 
          scrollWheelZoom={true} 
          style={{ height: '100%', width: '100%' }}
        >
          {mapType === 'standard' ? (
             <TileLayer
               attribution='&copy; OSM'
               url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
             />
          ) : (
             <TileLayer
               attribution='&copy; Esri'
               url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
             />
          )}

          <MapFlyTo coords={targetCoords} />
          {targetCoords && (
             <Marker position={targetCoords}>
                <Popup>Analyzed Region</Popup>
             </Marker>
          )}
        </MapContainer>

        {/* View Toggles & Draw Tools Overlay */}
        <div className="map-tools">
          <div className="tool-group glass-panel">
            <button 
              className={`tool-btn ${mapType === 'standard' ? 'active' : ''}`} 
              onClick={() => setMapType('standard')}
              title="Standard Map"
            >
              <MapIcon size={18} />
            </button>
            <button 
              className={`tool-btn ${mapType === 'satellite' ? 'active' : ''}`} 
              onClick={() => setMapType('satellite')}
              title="Satellite View"
            >
              <ImageIcon size={18} />
            </button>
          </div>

          <div className="tool-group glass-panel">
            <button className="tool-btn" title="Draw Area">
              <Crosshair size={18} />
            </button>
            <button className="tool-btn" title="Edit Area">
              <Edit3 size={18} />
            </button>
            <button className="tool-btn" title="Remove Area">
              <Trash2 size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Results Panel */}
      <div className={`results-panel glass-panel-heavy ${selectedRegion ? 'open' : ''}`}>
        {selectedRegion ? (
          <div className="results-content">
            <h2 className="results-title">{selectedRegion.name}</h2>
            <div className="analysis-tag">{activeTab} Analysis</div>

            <div className="score-card">
              <div className="score-value">{selectedRegion.score}</div>
              <div className="score-label">Aggregated Prediction Score</div>
            </div>

            <div className="results-section">
              <h3>Contributing Variables</h3>
              <ul>
                {selectedRegion.variables.map((v, i) => <li key={i}>{v}</li>)}
              </ul>
            </div>

            <div className="results-section">
              <h3>Environmental Indicators</h3>
              <p>{selectedRegion.indicators}</p>
            </div>

            <div className="results-section">
              <h3>Forecast Timeline & Trend</h3>
              <div style={{ width: '100%', height: 200, marginTop: '1rem' }}>
                <ResponsiveContainer>
                  <AreaChart data={mockChartData}>
                    <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                    <Area type="monotone" dataKey="val" stroke="var(--accent-base)" fill="var(--accent-glow)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        ) : (
          <div className="empty-results flex-center">
            <BarChart2 size={48} color="var(--text-muted)" />
            <p>Search a location or draw a polygon to generate analysis results.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchExplore;
