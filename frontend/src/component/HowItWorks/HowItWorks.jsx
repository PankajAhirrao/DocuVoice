// HowItWorks.jsx
import React from 'react';
import { MessageSquare } from 'lucide-react';
import './HowItWorks.css';

const HowItWorks = () => {
  return (
    <section className="how-it-works">
      <div className="section-container">
        <div className="section-header">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">
            Our workflow makes IEEE research paper analysis fast, structured, and interactive.
          </p>
        </div>
        
        <div className="steps-container">
          <div className="connection-line"></div>
          
          <div className="steps-grid">
            {/* Step 1 */}
            <div className="step step-right group">
              <div className="step-dot"></div>
              <span className="step-label">Step 1</span>
              <h3 className="step-title">Upload Your Paper</h3>
              <p className="step-text">Drag and drop your IEEE paper (PDF/DOCX) or browse your files to upload it securely.</p>
            </div>
            <div className="step-spacer"></div>
            
            {/* Step 2 */}
            <div className="step-spacer"></div>
            <div className="step step-left group">
              <div className="step-dot"></div>
              <span className="step-label">Step 2</span>
              <h3 className="step-title">Analyze Sections</h3>
              <p className="step-text">Select a paper section (abstract, methodology, results, etc.) and generate targeted insights in seconds.</p>
            </div>
            
            {/* Step 3 */}
            <div className="step step-right group">
              <div className="step-dot"></div>
              <span className="step-label">Step 3</span>
              <h3 className="step-title">Get Clear Summary</h3>
              <p className="step-text">Receive a concise summary with key contributions, technical keywords, and methodology highlights.</p>
            </div>
            <div className="step-spacer"></div>
            
            {/* Step 4 */}
            <div className="step-spacer"></div>
            <div className="step step-left group">
              <div className="step-dot"></div>
              <span className="step-label">Step 4</span>
              <h3 className="step-title">Chat & Ask Questions</h3>
              <p className="step-text">Ask questions about the paper and get accurate answers grounded in the uploaded content.</p>
              <div className="step-extra">
                <MessageSquare size={16} />
                <span>Interactive Q&A available</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;