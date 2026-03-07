import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import "./DocumentViewer.css";

const TABS = [
  { key: "summary", label: "Summary" },
  { key: "key_contributions", label: "Key Contributions" },
  { key: "technical_keywords", label: "Technical Keywords" },
  { key: "generated_questions", label: "Generated Questions" },
  { key: "methodology_insights", label: "Methodology Insights" },
  { key: "citations_extracted", label: "Citations Extracted" },
  { key: "read_aloud", label: "Read Aloud" },
];

function normalizeApiBase(url) {
  if (!url) return "";
  return url.endsWith("/") ? url : `${url}/`;
}

export default function DocumentViewer() {
  const apiUrl = normalizeApiBase(import.meta.env.VITE_API_URL);
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const uploadedFile = location?.state?.uploadedFile ?? null;
  const extractedText = location?.state?.ocrResult ?? "";
  const initialSummary = location?.state?.sometext ?? "";
  const selectedSection = location?.state?.section ?? "full_paper";

  const previewUrl = useMemo(() => {
    if (!uploadedFile) return "";
    if (uploadedFile.type !== "application/pdf") return "";
    return URL.createObjectURL(uploadedFile);
  }, [uploadedFile]);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const [activeTab, setActiveTab] = useState("summary");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(() => ({
    summary: initialSummary,
    key_contributions: null,
    technical_keywords: null,
    generated_questions: null,
    methodology_insights: null,
    citations_extracted: null,
    read_aloud: null,
  }));

  const speechRef = useRef(null);
  const authToken = useMemo(() => localStorage.getItem("authToken"), []);

  const commonHeaders = useMemo(() => {
    return authToken ? { Authorization: `Token ${authToken}` } : {};
  }, [authToken]);

  const contextPayload = useMemo(() => {
    return {
      paper_id: id,
      section: selectedSection,
      text: extractedText || undefined,
    };
  }, [id, selectedSection, extractedText]);

  const callApi = async (path, payload) => {
    if (!apiUrl) throw new Error("API URL is not configured");
    const url = `${apiUrl}${path}`.replace(/([^:]\/)\/+/g, "$1");
    const response = await axios.post(url, payload, { headers: commonHeaders });
    return response.data;
  };

  const fetchTabData = async (tabKey) => {
    // Avoid re-fetching if we already have data for the tab
    if (results[tabKey] !== null && results[tabKey] !== undefined && results[tabKey] !== "") {
      return;
    }

    setLoading(true);
    setError("");
    try {
      if (tabKey === "summary") {
        const data = await callApi("summarize/", contextPayload);
        setResults((prev) => ({ ...prev, summary: data?.summary ?? data?.summarized_text ?? "" }));
        return;
      }
      if (tabKey === "generated_questions") {
        const data = await callApi("generate-qa/", contextPayload);
        setResults((prev) => ({ ...prev, generated_questions: data?.questions ?? data ?? [] }));
        return;
      }
      if (tabKey === "technical_keywords") {
        const data = await callApi("extract-keywords/", contextPayload);
        setResults((prev) => ({ ...prev, technical_keywords: data?.keywords ?? data ?? [] }));
        return;
      }
      if (tabKey === "citations_extracted") {
        const data = await callApi("extract-citations/", contextPayload);
        setResults((prev) => ({ ...prev, citations_extracted: data?.citations ?? data ?? [] }));
        return;
      }
      if (tabKey === "key_contributions") {
        const data = await callApi("extract-contributions/", contextPayload);
        setResults((prev) => ({
          ...prev,
          key_contributions: data?.contributions ?? data?.key_contributions ?? data ?? [],
        }));
        return;
      }
      if (tabKey === "methodology_insights") {
        const data = await callApi("methodology-insights/", contextPayload);
        setResults((prev) => ({
          ...prev,
          methodology_insights: data?.insights ?? data?.methodology ?? data ?? "",
        }));
        return;
      }
      if (tabKey === "read_aloud") {
        const data = await callApi("read-aloud/", contextPayload);
        setResults((prev) => ({ ...prev, read_aloud: data ?? {} }));
        return;
      }
    } catch (e) {
      const message = e?.response?.data?.detail || e?.message || "Failed to fetch analysis";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTabData(activeTab);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, id, selectedSection]);

  const handleSpeak = () => {
    const textForSpeech =
      (typeof results.summary === "string" && results.summary.trim()) ||
      (typeof extractedText === "string" && extractedText.trim());

    if (!textForSpeech) return;

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(textForSpeech);
      speechRef.current = utter;
      window.speechSynthesis.speak(utter);
    }
  };

  const handleStopSpeak = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  };

  return (
    <div className="viewer-container">
      <button className="back-btn" onClick={() => navigate(-1)}>
        Back
      </button>

      <div className="split-pane">
        <div className="pane left-pane">
          <div className="pane-header">
            <h2 className="pane-title">Paper Preview</h2>
            <p className="pane-description">
              Viewing analysis for <strong>{selectedSection.replace(/_/g, " ")}</strong>
            </p>
          </div>
          <div className="pane-content">
            <div className="document-preview">
              {uploadedFile ? (
                <>
                  <div className="file-name">{uploadedFile.name}</div>
                  {uploadedFile.type === "application/pdf" && previewUrl ? (
                    <iframe
                      title="paper-preview"
                      className="file-preview"
                      src={previewUrl}
                    />
                  ) : (
                    <div className="preview-message">
                      Preview is available for PDFs. The extracted text is shown on the right.
                    </div>
                  )}
                </>
              ) : (
                <div className="preview-message">
                  Upload a paper from the dashboard to view the preview and AI insights here.
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="pane right-pane">
          <div className="pane-header">
            <h2 className="pane-title">Research Paper Analysis</h2>
            <p className="pane-description">
              Paper ID: <strong>{id}</strong>
            </p>

            <div className="tab-row">
              {TABS.map((t) => (
                <button
                  key={t.key}
                  type="button"
                  onClick={() => setActiveTab(t.key)}
                  className={`tab-btn ${activeTab === t.key ? "active" : ""}`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div className="pane-content">
            {loading && <div className="loading">Loading AI insights…</div>}
            {error && <div className="error">{error}</div>}

            {!loading && !error && (
              <>
                {activeTab === "summary" && (
                  <div className="ocr-result">
                    <h3 style={{ marginTop: 0 }}>Summary</h3>
                    <p className="ocr-text">{results.summary || "No summary available yet."}</p>
                  </div>
                )}

                {activeTab === "key_contributions" && (
                  <div className="ocr-result">
                    <h3 style={{ marginTop: 0 }}>Key Contributions</h3>
                    {Array.isArray(results.key_contributions) && results.key_contributions.length > 0 ? (
                      <ul>
                        {results.key_contributions.map((c, idx) => (
                          <li key={idx}>{typeof c === "string" ? c : JSON.stringify(c)}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="no-content">No contributions extracted yet.</div>
                    )}
                  </div>
                )}

                {activeTab === "technical_keywords" && (
                  <div className="ocr-result">
                    <h3 style={{ marginTop: 0 }}>Technical Keywords</h3>
                    {Array.isArray(results.technical_keywords) && results.technical_keywords.length > 0 ? (
                      <ul>
                        {results.technical_keywords.map((k, idx) => (
                          <li key={idx}>{typeof k === "string" ? k : JSON.stringify(k)}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="no-content">No keywords extracted yet.</div>
                    )}
                  </div>
                )}

                {activeTab === "generated_questions" && (
                  <div className="ocr-result">
                    <h3 style={{ marginTop: 0 }}>Generated Questions</h3>
                    {Array.isArray(results.generated_questions) && results.generated_questions.length > 0 ? (
                      <ul>
                        {results.generated_questions.map((q, idx) => (
                          <li key={idx}>{typeof q === "string" ? q : JSON.stringify(q)}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="no-content">No questions generated yet.</div>
                    )}
                  </div>
                )}

                {activeTab === "methodology_insights" && (
                  <div className="ocr-result">
                    <h3 style={{ marginTop: 0 }}>Methodology Insights</h3>
                    {typeof results.methodology_insights === "string" && results.methodology_insights ? (
                      <p className="ocr-text">{results.methodology_insights}</p>
                    ) : (
                      <div className="no-content">No methodology insights available yet.</div>
                    )}
                  </div>
                )}

                {activeTab === "citations_extracted" && (
                  <div className="ocr-result">
                    <h3 style={{ marginTop: 0 }}>Citations Extracted</h3>
                    {Array.isArray(results.citations_extracted) && results.citations_extracted.length > 0 ? (
                      <ul>
                        {results.citations_extracted.map((c, idx) => (
                          <li key={idx}>{typeof c === "string" ? c : JSON.stringify(c)}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="no-content">No citations extracted yet.</div>
                    )}
                  </div>
                )}

                {activeTab === "read_aloud" && (
                  <div className="ocr-result">
                    <h3 style={{ marginTop: 0 }}>Read Aloud</h3>
                    <p className="pane-description" style={{ marginTop: 0 }}>
                      Read the summary (or extracted text) aloud in your browser.
                    </p>
                    <div className="action-buttons">
                      <button className="action-btn chat-btn" onClick={handleSpeak}>
                        Play
                      </button>
                      <button className="action-btn ner-btn" onClick={handleStopSpeak}>
                        Stop
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}