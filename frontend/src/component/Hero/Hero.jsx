import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, BarChart2, Search } from 'lucide-react';
import './Hero.css';

const Hero = () => (
  <section className="hero-section">
    <div className="hero-bg">
      <div className="hero-bg-gradient"></div>
      <div className="hero-grid-overlay"></div>
    </div>
    <div className="hero-container">
      <div className="hero-content">
        <span className="hero-badge">
          <span className="badge-dot"></span>
          IEEE Research Paper Analysis
        </span>
        <h1 className="hero-title">
          <span className="title-line">Analyze IEEE Papers</span>
          <span className="title-highlight">With AI Precision</span>
        </h1>
        <p className="hero-subtitle">
          Upload IEEE research papers and instantly extract structured insights —
          authors, keywords, methodology, results, citations, and more.
        </p>
        <div className="hero-buttons">
          <Link to="/register">
            <button className="btn btn-primary">
              <span className="btn-content">Analyze a Paper <ArrowRight size={16} className="btn-arrow" /></span>
            </button>
          </Link>
          <Link to="/login">
            <button className="btn btn-outline">Sign In</button>
          </Link>
        </div>
      </div>

      <div className="hero-features">
        {[
          { icon: <BookOpen size={22} />, title: "Structured Extraction", text: "Auto-extract abstract, methodology, results, and conclusions from IEEE PDFs." },
          { icon: <Search size={22} />, title: "Entity Recognition", text: "Identify authors, institutions, citations, datasets, and technical terms." },
          { icon: <BarChart2 size={22} />, title: "Research Insights", text: "Ask questions about the paper and get precise, context-aware answers." },
        ].map((f, i) => (
          <div key={i} className="feature-card">
            <div className="feature-icon">{f.icon}</div>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-text">{f.text}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default Hero;