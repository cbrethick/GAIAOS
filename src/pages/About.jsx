import { Github, Linkedin, Globe, Mail } from 'lucide-react';
import './About.css';

const About = () => {
  return (
    <div className="container about-page">
      <div className="profile-card glass-panel-heavy">
        <div className="profile-layout">
          <div className="photo-container">
            <img src="/rethick.png" alt="Rethick CB" className="profile-photo" />
          </div>
          <div className="profile-info">
            <h1 className="profile-name">Rethick CB</h1>
            <p className="profile-title">
              Computer Science student focused on artificial intelligence, 
              data science, and planetary-scale environmental modeling.
            </p>
          </div>
        </div>

        <div className="project-description">
          <h2>About GaiaOS</h2>
          <p>
            GaiaOS is an open Earth digital twin system. The goal of this project is to aggregate 
            isolated environmental data streams into a single, unified intelligence layer. By providing 
            real-time predictions and uncovering obscure cross-system patterns, GaiaOS seeks to equip 
            scientists and policymakers with the insights necessary to mitigate the impacts of acute 
            climate events and urban challenges.
          </p>
        </div>

        <div className="links-section">
          <a href="https://github.com/cbrethick" target="_blank" rel="noopener noreferrer" className="social-link btn-outline">
            <Github size={20} />
            GitHub
          </a>
          <a href="https://www.linkedin.com/in/rethick-cb/" target="_blank" rel="noopener noreferrer" className="social-link btn-outline">
            <Linkedin size={20} />
            LinkedIn
          </a>
          <a href="https://rethickcb.com" target="_blank" rel="noopener noreferrer" className="social-link btn-outline">
            <Globe size={20} />
            Website
          </a>
          <a href="mailto:rethickcb2007@gmail.com" className="social-link btn-outline">
            <Mail size={20} />
            Email
          </a>
        </div>
      </div>
    </div>
  );
};

export default About;
