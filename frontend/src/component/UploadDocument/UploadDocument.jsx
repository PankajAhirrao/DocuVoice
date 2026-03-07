// UploadDocument.jsx
import React, { useState } from "react";
import { Upload } from "lucide-react";
import "./UploadDocument.css";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const UploadDocument = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [selectedSection, setSelectedSection] = useState("full_paper");
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);

  const toastModel = ({ title, description, variant }) => {
    console.log(`${title}: ${description} ${variant ? `(${variant})` : ""}`);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toastModel({
        title: "No file selected",
        description: "Please select a research paper to analyze",
        variant: "destructive",
      });
      toast.error("Please select a research paper to analyze", {
        position: "top-right",
        autoClose: 3000,
      });
      return;
    }

    setProcessing(true);
    setProgress(0);
    const authToken = localStorage.getItem("authToken");

    if (!authToken) {
      toast.error("Authentication token not found. Please log in.", {
        position: "top-right",
        autoClose: 3000,
      });
      setProcessing(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("section", selectedSection);

    try {
      const response = await axios.post(apiUrl + "users/upload/", formData, {
        headers: {
          "Authorization": `Token ${authToken}`,
          "Content-Type": "multipart/form-data",
        },
      });

      console.log(response.data);

      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setProcessing(false);
            toast.success("Your paper has been analyzed successfully", {
              position: "top-right",
              autoClose: 3000,
            });
            const viewerId =
              response?.data?.id ??
              response?.data?.document_id ??
              response?.data?.paper_id ??
              "latest";

            navigate(`/viewer/${viewerId}`, {
              state: {
                uploadedFile: file,
                ocrResult: response.data.extracted_text || "OCR text not available",
                sometext: response.data.summarized_text || "Summarized text",
                section: selectedSection,
              },
            });
            return 100;
          }
          return prev + 10;
        });
      }, 500);
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Error processing document: " + error.message, {
        position: "top-right",
        autoClose: 3000,
      });
      setProcessing(false);
    }
  };

  return (
    <div className="upload-card">
      <div className="card-header">
        <h2 className="card-title">
          <Upload size={20} />
          Upload IEEE Research Paper
        </h2>
        <p className="card-description">
          Upload an IEEE paper to extract structured insights and summaries
        </p>
      </div>
      <div className="card-content">
        <form onSubmit={handleSubmit}>
          <div className="section-select">
            <label
              htmlFor="paper-section"
              className="section-label"
            >
              Select Section to Analyze
            </label>
            <select
              id="paper-section"
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              disabled={processing}
              className="section-dropdown"
            >
              <option value="full_paper">Full Paper</option>
              <option value="title">Title</option>
              <option value="abstract">Abstract</option>
              <option value="introduction">Introduction</option>
              <option value="related_work">Related Work</option>
              <option value="methodology">Methodology</option>
              <option value="dataset_experimental_setup">Dataset / Experimental Setup</option>
              <option value="results">Results</option>
              <option value="discussion">Discussion</option>
              <option value="conclusion">Conclusion</option>
              <option value="references">References</option>
              <option value="citations">Citations</option>
              <option value="figures_tables">Figures &amp; Tables</option>
            </select>
          </div>

          <div className="upload-area">
            <label htmlFor="document" className="upload-label">
              <Upload size={32} />
              <span>
                {file ? file.name : "Click to select or drag and drop"}
              </span>
              <span className="upload-info">
                Supports PDF and DOCX (Max 10MB)
              </span>
            </label>
            <input
              id="document"
              type="file"
              className="upload-input"
              accept=".pdf,.docx,.doc"
              onChange={handleFileChange}
            />
          </div>

          {processing && (
            <div className="progress-section">
              <div className="progress-header">
                <span>Processing document...</span>
                <span>{progress}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          )}

          <button
            type="submit"
            className="submit-btn"
            disabled={!file || processing}
          >
            {processing ? "Processing..." : "Analyze Paper"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UploadDocument;