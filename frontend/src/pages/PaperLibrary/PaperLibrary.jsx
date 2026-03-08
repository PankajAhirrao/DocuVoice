import Stats from "../../component/Stats/Stats";
import DocumentHistory from "../../component/DocumentHistory/DocumentHistory";
import "./PaperLibrary.css";

export default function PaperLibrary() {
  return (
    <div className="paper-library-page">
      <div className="paper-library-header">
        <h1 className="page-title">Paper Library</h1>
        <p className="page-subtitle">Browse your uploaded papers and quick account stats.</p>
      </div>

      <div className="paper-library-grid">
        <section className="paper-library-stats">
          <Stats />
        </section>
        <section className="paper-library-history">
          <DocumentHistory />
        </section>
      </div>
    </div>
  );
}
