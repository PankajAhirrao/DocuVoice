import React from 'react';
import { FileSearch, Tag, Users, Quote, FlaskConical, BarChart2 } from 'lucide-react';
import './Features.css';

const features = [
  { icon: <FileSearch />, title: "Abstract & Section Extraction", desc: "Parses IEEE paper structure — abstract, intro, methodology, results, conclusion, and references." },
  { icon: <Tag />, title: "Keyword & Topic Detection", desc: "Identifies IEEE index terms, technical keywords, and research domains automatically." },
  { icon: <Users />, title: "Author & Institution NER", desc: "Extracts all authors, affiliated institutions, departments, and corresponding author details." },
  { icon: <Quote />, title: "Citation Parsing", desc: "Structures references into DOI, author, year, journal, and volume for downstream use." },
  { icon: <FlaskConical />, title: "Methodology Summarization", desc: "Condenses experimental setup, datasets, evaluation metrics, and proposed approach." },
  { icon: <BarChart2 />, title: "Results & Contribution Summary", desc: "Highlights key numerical results, benchmarks, and core contributions by the authors." },
];

const Features = () => (
  <section className="features-section">
    <div className="features-top-line"></div>
    <div className="features-container">
      <div className="features-header">
        <span className="features-badge">Capabilities</span>
        <h2 className="features-title">Built for IEEE Paper Analysis</h2>
        <p className="features-subtitle">
          Every feature is designed around the IEEE paper format — from double-column PDFs to structured reference lists.
        </p>
      </div>
      <div className="features-grid">
        {features.map((f, i) => (
          <div key={i} className="feat-card" style={{ animationDelay: `${i * 80}ms` }}>
            <div className="feat-icon">{f.icon}</div>
            <h3 className="feat-title">{f.title}</h3>
            <p className="feat-desc">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
    <div className="features-bottom-line"></div>
  </section>
);

export default Features;