import { Link, useLocation } from 'react-router-dom';
import { Globe, Compass, LayoutDashboard, Microscope, User } from 'lucide-react';
import './Navigation.css';

const Navigation = () => {
  const location = useLocation();

  const navLinks = [
    { name: 'Home', path: '/', icon: <Globe size={18} /> },
    { name: 'Explore', path: '/explore', icon: <Compass size={18} /> },
    { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={18} /> },
    { name: 'Research', path: '/research', icon: <Microscope size={18} /> },
    { name: 'About', path: '/about', icon: <User size={18} /> },
  ];

  return (
    <nav className="top-nav glass-panel-heavy">
      <div className="nav-container flex-between">
        <Link to="/" className="nav-logo">
          GaiaOS
        </Link>
        <div className="nav-links">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`nav-link flex-center ${location.pathname === link.path ? 'active' : ''}`}
            >
              {link.icon}
              <span>{link.name}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
