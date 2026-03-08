import UploadDocument from "../../component/UploadDocument/UploadDocument";
import "./UploadPaper.css";

export default function UploadPaper() {
  return (
    <div className="upload-paper-page">
      <div className="upload-paper-header">
        <h1 className="page-title">Upload Paper</h1>
        <p className="page-subtitle">Upload an IEEE research paper and generate analysis insights.</p>
      </div>

      <section className="upload-paper-content">
        <UploadDocument />
      </section>
    </div>
  );
}
