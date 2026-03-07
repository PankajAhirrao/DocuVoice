import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../../component/Navbar/Navbar';
import Hero from '../../component/Hero/Hero';
import Features from '../../component/Features/Features';
import { ArrowRight, BookOpen } from 'lucide-react';
import './Index.css';

const Index = () => {
  useEffect(() => { window.scrollTo(0, 0); }, []);

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="main-content">
        <Hero />
        <Features />

        {/* CTA Section */}
        <section className="cta-section">
          <div className="section-container">
            <div className="cta-content">
              <div className="cta-glow"></div>
              <div className="cta-badge">Start Analyzing</div>
              <h2 className="cta-title">Ready to Extract Insights from IEEE Papers?</h2>
              <p className="cta-text">
                Upload any IEEE Xplore paper and get instant structured analysis —
                authors, keywords, methodology, results, and citations in seconds.
              </p>
              <div className="cta-buttons">
                <Link to="/register">
                  <button className="btn btn-primary">
                    <span className="btn-content">
                      Upload Your First Paper
                      <ArrowRight size={15} className="btn-arrow" />
                    </span>
                  </button>
                </Link>
                <Link to="/login">
                  <button className="btn btn-outline">Sign In</button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="section-container">
          <div className="footer-content">
            <div className="footer-left">
              <Link to="/" className="footer-logo">
                <div className="logo-icon"><BookOpen size={15} /></div>
                <span className="logo-text">IEEE<span className="logo-accent">Analyze</span></span>
              </Link>
              <p className="footer-text">AI-powered analysis for IEEE research papers.</p>
            </div>
            <div className="footer-right">
              <div className="footer-links">
                <Link to="/about" className="footer-link">About</Link>
                <Link to="/features" className="footer-link">Features</Link>
                <Link to="/contact" className="footer-link">Contact</Link>
              </div>
              <p className="footer-copyright">© {new Date().getFullYear()} IEEEAnalyze. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;