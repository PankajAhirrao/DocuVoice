// Instructions.jsx
import React from 'react';
import { Info } from 'lucide-react';
import './Instructions.css';

const Instructions = () => {
  return (
    <div className="instructions-card">
      <div className="card-header">
        <h2 className="card-title">
          <Info size={20} />
          How It Works
        </h2>
      </div>
      <div className="card-content">
        <div className="instruction-item">
          <div className="step-number">1</div>
          <h3>Upload Paper</h3>
          <p>Upload an IEEE research paper in PDF or DOCX format.</p>
        </div>
        <div className="instruction-item">
          <div className="step-number">2</div>
          <h3>Analyze Sections</h3>
          <p>Choose a section (abstract, methodology, results, etc.) for targeted analysis.</p>
        </div>
        <div className="instruction-item">
          <div className="step-number">3</div>
          <h3>Get Summary</h3>
          <p>Get structured summaries, contributions, keywords, and citations.</p>
        </div>
        <div className="instruction-item">
          <div className="step-number">4</div>
          <h3>Chat & Learn</h3>
          <p>Ask questions about the paper and explore methodology and results quickly.</p>
        </div>
      </div>
    </div>
  );
};

export default Instructions;