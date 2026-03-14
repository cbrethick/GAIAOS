import { useState } from 'react';
import { MapContainer, TileLayer, useMap, ZoomControl, Rectangle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Activity, Thermometer, CloudRain, Flame, Car } from 'lucide-react';
import './LiveEarthMap.css';

import { Search } from 'lucide-react';

const modules = [
  { id: 'flood', name: 'Flood', icon: CloudRain, color: 'var(--color-safe)' },
  { id: 'climate', name: 'Climate', icon: Thermometer, color: 'var(--color-cold)' },
  { id: 'crop', name: 'Crop Yield', icon: Activity, color: 'var(--color-caution)' },
  { id: 'wildfire', name: 'Wildfire', icon: Flame, color: 'var(--color-danger)' },
  { id: 'traffic', name: 'Traffic', icon: Car, color: 'var(--color-safe)' }
];

const mockData = {
  name: "Sector 7G District",
  score: 84,
  factors: ["High soil moisture content", "Expected dense rainfall in 48h", "Poor drainage infra"],
  trend: [30, 45, 60, 84, 90, 85, 70]
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

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery) return;
    
    setIsSearching(true);
    try {
      // Use Nominatim from OpenStreetMap to geocode real locations
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

        setSelectedRegion({
          name: result.display_name.split(',')[0],
          score: Math.floor(Math.random() * 40) + 40, // Simulated prediction score 40-80
          factors: ["Localized surface metrics", "Recent sensor anomalies observed"],
          trend: [50, 60, 65, 70, 72, 72, 75]
        });
      } else {
        alert("Location not found on Earth.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to search location.");
    } finally {
      setIsSearching(false);
    }
  };

  // Determine Map Tile Url Based on active Module distinctly
  const getMapTile = () => {
    if (mapStyle === 'map') {
      return "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}";
    }
    if (mapStyle === 'satellite') {
      return "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}";
    }

    switch (activeModule) {
      case 'flood':
        // CartoDB Voyager (Light, Clean map with blue water focus and labels)
        return "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
      case 'climate':
        // Stadia Alidade Smooth Dark (Dark theme map with subtle labels)
        return "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png";
      case 'crop':
        // Esri World Imagery + labels via generic hybrid (Looks distinctly satellite green)
        return "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
      case 'wildfire':
        // OpenTopoMap (Topographic with heavy contour lines and labels)
        return "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png";
      case 'traffic':
        // Standard OSM Default (Bright, detailed roadmap)
        return "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
      default:
        return "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    }
  };

  const MapFlyTo = ({ coords, bounds }) => {
    const map = useMap();
    if (bounds) {
      map.fitBounds(bounds, { padding: [50, 50], animate: true, duration: 1.5 });
    } else if (coords) {
      map.flyTo(coords, 10, { duration: 1.5 });
    }
    return null;
  };

  return (
    <div className="map-page-container">
      {/* Module Controls Layer */}
      <div className="module-controls glass-panel">
        <h3 className="controls-title">Prediction Modules</h3>
        {modules.map((mod) => (
          <button
            key={mod.id}
            className={`module-btn ${activeModule === mod.id ? 'active' : ''}`}
            onClick={() => setActiveModule(mod.id)}
            style={{ '--module-color': mod.color }}
          >
            <mod.icon size={20} />
            <span>{mod.name}</span>
          </button>
        ))}
      </div>
      {/* Search Bar - Bottom */}
      <div className="explore-search-container glass-panel">
        <form className="search-bar" onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={20} className="search-icon" style={{ color: 'var(--text-secondary)' }} />
          <input 
            type="text" 
            placeholder="Search full Earth..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: '1.1rem', outline: 'none' }}
          />
          <button type="submit" disabled={isSearching} className="btn-primary" style={{ padding: '0.4rem 1rem', borderRadius: '4px', border: 'none', cursor: 'pointer', color: '#fff' }}>
            {isSearching ? '...' : 'Search'}
          </button>
        </form>
      </div>

      {/* Map View Toggle - Top Right */}
      <div className="map-view-toggle glass-panel">
        <button 
          className={`toggle-btn ${mapStyle === 'auto' ? 'active' : ''}`}
          onClick={() => setMapStyle('auto')}
        >
          Auto
        </button>
        <button 
          className={`toggle-btn ${mapStyle === 'map' ? 'active' : ''}`}
          onClick={() => setMapStyle('map')}
        >
          Map
        </button>
        <button 
          className={`toggle-btn ${mapStyle === 'satellite' ? 'active' : ''}`}
          onClick={() => setMapStyle('satellite')}
        >
          Satellite
        </button>
      </div>

      {/* The Map itself */}
      <div className="map-wrapper">
        <MapContainer 
          center={[20, 0]} 
          zoom={3} 
          scrollWheelZoom={true} 
          zoomControl={false}
          style={{ height: '100%', width: '100%' }}
        >
          <ZoomControl position="bottomright" />
          <MapFlyTo coords={targetCoords} bounds={targetBounds} />
          
          {targetBounds && (
            <Rectangle 
              bounds={targetBounds}
              pathOptions={{ color: 'red', weight: 4, dashArray: '5, 10', fillOpacity: 0.1 }}
            />
          )}

          {/* Dynamic Google Maps tile layer */}
          <TileLayer
            key={activeModule} // forces re-render when URL changes
            attribution='&copy; Google Maps'
            url={getMapTile()}
          />
        </MapContainer>
      </div>

      {/* Forecast Timeline Slider */}
      <div className="timeline-container glass-panel">
        <div className="flex-between timeline-header">
          <span>Current Condition</span>
          <span>+ {timeline} Hours Forecast</span>
          <span>+ 72 Hours</span>
        </div>
        <input 
          type="range" 
          min="0" 
          max="72" 
          step="6"
          value={timeline} 
          onChange={(e) => setTimeline(e.target.value)}
          className="timeline-slider"
        />
      </div>

      {/* Side Information Panel */}
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
                <span className="score-val" style={{ 
                  color: selectedRegion.score > 80 ? 'var(--color-danger)' : 
                         selectedRegion.score > 50 ? 'var(--color-caution)' : 'var(--color-safe)' 
                }}>
                  {selectedRegion.score}
                </span>
                <span className="score-max">/ 100</span>
              </div>
            </div>

            <div className="panel-section">
              <h3>Main Contributing Factors</h3>
              <ul className="factors-list">
                {selectedRegion.factors.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>

            <div className="panel-section">
              <h3>Trend Over Time</h3>
              <div className="trend-chart-ph">
                {/* CSS based sparkline placeholder */}
                <div className="sparkline">
                   {selectedRegion.trend.map((val, i) => (
                      <div key={i} className="bar" style={{ height: `${val}%` }}></div>
                   ))}
                </div>
              </div>
              <p className="trend-desc">Historical pattern vs current trajectory shows elevating risk factors in the next 48h.</p>
            </div>
          </>
        ) : (
          <div className="empty-panel flex-center">
            <p>Select a region on the map to view detailed AI predictions.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveEarthMap;
