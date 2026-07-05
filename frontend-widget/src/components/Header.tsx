import React from 'react';
import logoImg from '../assets/logo.png';
import './Header.css';

interface HeaderProps {
  onNavigateHome: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onNavigateHome }) => {
  return (
    <header className="safex-header-container">
      <div className="top-bar">
        <div className="top-bar-content">
          <span>CONTACT@SAFEXSOLUTIONS.COM</span>
        </div>
      </div>
      <nav className="main-nav">
        <div className="nav-content">
          <div className="logo" onClick={onNavigateHome} style={{ cursor: 'pointer' }}>
            <img src={logoImg} alt="SafeX Solutions" className="header-logo-img" />
          </div>
          
          <ul className="nav-links">
            <li onClick={onNavigateHome}>Home</li>
            <li className="active">About</li>
            <li>Services ▾</li>
            <li>Contact</li>
            <li>Trust</li>
            <li>Blog</li>
          </ul>

          <div className="social-icons">
            {/* Social icons placeholder */}
            <span style={{cursor: 'pointer'}}>FB</span>
            <span style={{cursor: 'pointer'}}>IG</span>
            <span style={{cursor: 'pointer'}}>IN</span>
            <span style={{cursor: 'pointer'}}>X</span>
          </div>
        </div>
      </nav>
    </header>
  );
};
