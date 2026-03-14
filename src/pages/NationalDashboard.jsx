import { useState } from 'react';
import { ShieldAlert, CloudRain, Sprout, Flame, Car, Building2, ArrowRight } from 'lucide-react';
import './NationalDashboard.css';

const indicators = [
  { title: "Flood Alerts", value: "14 Active", icon: CloudRain, color: "var(--color-safe)", trend: "+2" },
  { title: "Monsoon Status", value: "Normal", icon: CloudRain, color: "var(--color-cold)", trend: "Expected" },
  { title: "Crop Risk Regions", value: "High Stress", icon: Sprout, color: "var(--color-danger)", trend: "Critical" },
  { title: "Active Wildfire Zones", value: "3 Regions", icon: Flame, color: "var(--color-extreme)", trend: "Elevated" },
  { title: "Major Traffic Congestion", value: "8 Corridors", icon: Car, color: "var(--color-caution)", trend: "Peaking" },
  { title: "Urban Expansion Trends", value: "+4.2% YoY", icon: Building2, color: "var(--accent-base)", trend: "Accelerating" },
];

const mockAlerts = [
  { id: 1, region: "Northern River Basin", module: "Flood", severity: 92, pop: "1.2M", severityLabel: "Critical" },
  { id: 2, region: "Western Forests", module: "Wildfire", severity: 88, pop: "400K", severityLabel: "Severe" },
  { id: 3, region: "Central Farmlands", module: "Crop Yield", severity: 75, pop: "2.1M", severityLabel: "High" },
  { id: 4, region: "Metro Highway A4", module: "Traffic", severity: 60, pop: "800K", severityLabel: "Moderate" },
  { id: 5, region: "Eastern Coastal", module: "Climate", severity: 45, pop: "3.5M", severityLabel: "Monitor" },
];

const NationalDashboard = () => {
  const [sortField, setSortField] = useState('severity');
  const [sortAsc, setSortAsc] = useState(false);

  const sortedAlerts = [...mockAlerts].sort((a, b) => {
    if (sortField === 'region' || sortField === 'module') {
      return sortAsc ? a[sortField].localeCompare(b[sortField]) : b[sortField].localeCompare(a[sortField]);
    } else {
      return sortAsc ? a[sortField] - b[sortField] : b[sortField] - a[sortField]; // numeric sort for severity
    }
  });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="dashboard-container container">
      <header className="dashboard-header">
        <h1>National System Dashboard</h1>
        <p>Comprehensive overview of all environmental and urban AI models.</p>
      </header>

      {/* Key Indicators */}
      <section className="indicators-grid">
        {indicators.map((ind, i) => (
          <div key={i} className="indicator-card glass-panel">
            <div className="indicator-header">
              <ind.icon size={24} style={{ color: ind.color }} />
              <span className="indicator-trend" style={{ color: ind.color }}>{ind.trend}</span>
            </div>
            <div className="indicator-body">
              <h3 className="indicator-val" style={{ color: ind.color }}>{ind.value}</h3>
              <p className="indicator-title">{ind.title}</p>
            </div>
          </div>
        ))}
      </section>

      {/* Risk Ranking Table */}
      <section className="risk-table-section glass-panel">
        <div className="section-header flex-between">
          <h2>Significant Alert Regions</h2>
          <ShieldAlert size={24} color="var(--color-danger)" />
        </div>
        
        <div className="table-wrapper">
          <table className="risk-table">
            <thead>
              <tr>
                <th onClick={() => handleSort('region')}>Region {sortField==='region' && (sortAsc ? '↑' : '↓')}</th>
                <th onClick={() => handleSort('module')}>System {sortField==='module' && (sortAsc ? '↑' : '↓')}</th>
                <th onClick={() => handleSort('severity')}>Severity {sortField==='severity' && (sortAsc ? '↑' : '↓')}</th>
                <th>Affected Population</th>
              </tr>
            </thead>
            <tbody>
              {sortedAlerts.map(alert => (
                <tr key={alert.id}>
                  <td>{alert.region}</td>
                  <td><span className={`tag tag-${alert.module.toLowerCase().replace(' ', '')}`}>{alert.module}</span></td>
                  <td>
                    <div className="severity-bar-container">
                      <div className="severity-bar" style={{ 
                        width: `${alert.severity}%`,
                        backgroundColor: alert.severity > 80 ? 'var(--color-danger)' : alert.severity > 60 ? 'var(--color-caution)' : 'var(--color-cold)'
                      }}></div>
                      <span className="severity-text">{alert.severityLabel} ({alert.severity}/100)</span>
                    </div>
                  </td>
                  <td className="pop-exposure">{alert.pop}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Cross-System Insights */}
      <section className="insights-section glass-panel">
        <h2>Cross-System AI Insights</h2>
        <p className="insights-desc">Patterns and causal links discovered by GaiaOS connecting multiple environmental variables.</p>
        
        <div className="insight-flow">
          <div className="flow-node highlight-cold">Ocean Temperature Anomaly</div>
          <ArrowRight className="flow-arrow" />
          <div className="flow-node highlight-base">Atmospheric Circulation Shift</div>
          <ArrowRight className="flow-arrow" />
          <div className="flow-node highlight-caution">Delayed Rainfall Patterns</div>
          <ArrowRight className="flow-arrow" />
          <div className="flow-node highlight-danger">Vegetation Stress Signals</div>
        </div>

        <div className="insight-flow">
          <div className="flow-node highlight-caution">Urban Sprawl (+4%)</div>
          <ArrowRight className="flow-arrow" />
          <div className="flow-node highlight-base">Decreased Permeable Surface</div>
          <ArrowRight className="flow-arrow" />
          <div className="flow-node highlight-safe">Flash Flood Vulnerability High</div>
          <ArrowRight className="flow-arrow" />
          <div className="flow-node highlight-danger">Increased Traffic Gridlock Risk</div>
        </div>
      </section>
    </div>
  );
};

export default NationalDashboard;
