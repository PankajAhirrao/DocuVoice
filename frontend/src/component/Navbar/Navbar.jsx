import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AlignRight, X, BookOpen } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => { setIsOpen(false); }, [location.pathname]);

  return (
    <header className={`navbar ${isScrolled ? 'navbar-scrolled' : ''}`}>
      <div className="navbar-container">
        <nav className="navbar-nav">
          <Link to="/" className="navbar-logo">
            <div className="logo-icon"><BookOpen size={18} /></div>
            <span className="logo-text">DocuVoice <span className="logo-accent">AI</span></span>
          </Link>

          <div className="nav-links desktop-nav">
            <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>Home</Link>
            <Link to="/dashboard" className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}>Dashboard</Link>
          </div>

          <div className="auth-buttons desktop-nav">
            <Link to="/login"><button className="btn btn-ghost">Sign In</button></Link>
            <Link to="/register"><button className="btn btn-primary">Get Started</button></Link>
          </div>

          <button onClick={() => setIsOpen(!isOpen)} className="mobile-menu-btn">
            {isOpen ? <X size={24} /> : <AlignRight size={24} />}
          </button>
        </nav>
      </div>

      <div className={`mobile-menu ${isOpen ? 'mobile-menu-open' : ''}`}>
        <div className="mobile-menu-content">
          <Link to="/" className="mobile-nav-link">Home</Link>
          <Link to="/dashboard" className="mobile-nav-link">Dashboard</Link>
          <div className="mobile-auth-section">
            <Link to="/login"><button className="btn btn-ghost mobile-btn">Sign In</button></Link>
            <Link to="/register"><button className="btn btn-primary mobile-btn">Get Started</button></Link>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;