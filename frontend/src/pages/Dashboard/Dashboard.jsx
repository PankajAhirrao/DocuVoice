import UploadDocument from "../../component/UploadDocument/UploadDocument";
import DocumentHistory from "../../component/DocumentHistory/DocumentHistory";
import Stats from "../../component/Stats/Stats";

import "./Dashboard.css";

export default function Dashboard() {
  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1 className="page-title">IEEE Paper Analyzer</h1>
        <p className="page-subtitle">
          Analyze IEEE research papers using AI to extract summaries, technical insights, and key contributions.
        </p>
      </div>

      <div className="dashboard-grid">
        <section className="dashboard-stats">
          <Stats />
        </section>

        <section className="dashboard-upload">
          <UploadDocument />
        </section>

        <section className="dashboard-history">
          <DocumentHistory />
        </section>
      </div>
    </div>
  );
}
