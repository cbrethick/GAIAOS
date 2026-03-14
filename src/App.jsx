import { Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';

// Placeholder Pages
import LandingPage from './pages/LandingPage';
import LiveEarthMap from './pages/LiveEarthMap';
import SearchExplore from './pages/SearchExplore';
import NationalDashboard from './pages/NationalDashboard';
import ResearchMethodology from './pages/ResearchMethodology';
import About from './pages/About';

function App() {
  return (
    <>
      <Navigation />
      <main>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/explore" element={<LiveEarthMap />} />
          <Route path="/search" element={<SearchExplore />} />
          <Route path="/dashboard" element={<NationalDashboard />} />
          <Route path="/research" element={<ResearchMethodology />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
