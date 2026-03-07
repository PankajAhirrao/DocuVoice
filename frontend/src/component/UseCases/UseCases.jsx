// UseCases.jsx
import React from 'react';
import { Check, FileText, Globe, Lightbulb } from 'lucide-react';
import './UseCases.css';

const UseCases = () => {
  return (
    <section className="use-cases">
      <div className="section-container">
        <div className="section-header">
          <h2 className="section-title">Use Cases</h2>
          <p className="section-subtitle">
            See how researchers and students accelerate their IEEE paper workflow using AI.
          </p>
        </div>
        
        <div className="use-cases-grid">
          <div className="use-case-card">
            <div className="use-case-icon">
              <FileText className="icon" size={24} />
            </div>
            <h3 className="use-case-title">Literature Reviews</h3>
            <p className="use-case-text">
              Summarize abstracts, extract contributions, and compare methods across many IEEE papers quickly.
            </p>
            <ul className="use-case-list">
              <li>
                <Check className="check-icon" size={18} />
                <span>Fast abstract + intro scanning</span>
              </li>
              <li>
                <Check className="check-icon" size={18} />
                <span>Method & dataset extraction</span>
              </li>
              <li>
                <Check className="check-icon" size={18} />
                <span>Citation & reference parsing</span>
              </li>
            </ul>
          </div>
          
          <div className="use-case-card">
            <div className="use-case-icon">
              <Globe className="icon" size={24} />
            </div>
            <h3 className="use-case-title">Reproducibility Checks</h3>
            <p className="use-case-text">
              Identify datasets, experimental setup, metrics, and results to validate claims and replicate experiments.
            </p>
            <ul className="use-case-list">
              <li>
                <Check className="check-icon" size={18} />
                <span>Experimental setup summarization</span>
              </li>
              <li>
                <Check className="check-icon" size={18} />
                <span>Metrics and benchmark extraction</span>
              </li>
              <li>
                <Check className="check-icon" size={18} />
                <span>Results and limitation highlights</span>
              </li>
            </ul>
          </div>
          
          <div className="use-case-card">
            <div className="use-case-icon">
              <Lightbulb className="icon" size={24} />
            </div>
            <h3 className="use-case-title">Project Ideation</h3>
            <p className="use-case-text">
              Extract gaps, open questions, and related work signals to find your next experiment or thesis topic.
            </p>
            <ul className="use-case-list">
              <li>
                <Check className="check-icon" size={18} />
                <span>Key contribution detection</span>
              </li>
              <li>
                <Check className="check-icon" size={18} />
                <span>Technical keyword clustering</span>
              </li>
              <li>
                <Check className="check-icon" size={18} />
                <span>Question generation for reading</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};

export default UseCases;