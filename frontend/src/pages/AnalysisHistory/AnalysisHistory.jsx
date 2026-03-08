import DocumentHistory from "../../component/DocumentHistory/DocumentHistory";
import "./AnalysisHistory.css";

export default function AnalysisHistory() {
  return (
    <div className="analysis-history-page">
      <div className="analysis-history-header">
        <h1 className="page-title">Analysis History</h1>
        <p className="page-subtitle">Review your previously analyzed papers and reopen results.</p>
      </div>

      <section className="analysis-history-content">
        <DocumentHistory />
      </section>
    </div>
  );
}
