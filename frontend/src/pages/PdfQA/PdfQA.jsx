import { useState, useRef } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { Mic, Square, Upload, Send } from "lucide-react";
import "./PdfQA.css";

export default function PdfQA() {
  const apiUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/").replace(/\/?$/, "/");
  const [documentId, setDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [recording, setRecording] = useState(false);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      toast.error("Choose a PDF file");
      return;
    }
    const fd = new FormData();
    fd.append("pdf", file);
    setUploading(true);
    setDocumentId("");
    setAnswer("");
    setAudioUrl("");
    try {
      const { data } = await axios.post(`${apiUrl}upload-pdf/`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setDocumentId(data.document_id);
      toast.success(`Indexed ${data.chunks} chunks`);
    } catch (err) {
      toast.error(err.response?.data?.error || "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const ask = async (extraFormData) => {
    if (!documentId) {
      toast.error("Upload a PDF first");
      return;
    }
    const fd = extraFormData || new FormData();
    if (!extraFormData) {
      fd.append("document_id", documentId);
      fd.append("question", question);
    } else if (!fd.has("document_id")) {
      fd.append("document_id", documentId);
    }
    setAsking(true);
    setAnswer("");
    setAudioUrl("");
    try {
      const { data } = await axios.post(`${apiUrl}ask-question/`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAnswer(data.answer || "");
      setAudioUrl(data.audio_url || "");
      if (data.question_used) setQuestion(data.question_used);
      toast.success("Answer ready");
    } catch (err) {
      toast.error(err.response?.data?.error || "Ask failed");
    } finally {
      setAsking(false);
    }
  };

  const startRec = async () => {
    if (!documentId) {
      toast.error("Upload a PDF first");
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    chunksRef.current = [];
    const mr = new MediaRecorder(stream);
    mediaRef.current = mr;
    mr.ondataavailable = (ev) => {
      if (ev.data.size) chunksRef.current.push(ev.data);
    };
    mr.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(chunksRef.current, { type: mr.mimeType || "audio/webm" });
      const fd = new FormData();
      fd.append("document_id", documentId);
      fd.append("audio", blob, "question.webm");
      await ask(fd);
    };
    mr.start();
    setRecording(true);
  };

  const stopRec = () => {
    const mr = mediaRef.current;
    if (mr && mr.state !== "inactive") mr.stop();
    setRecording(false);
  };

  return (
    <div className="pdfqa-page">
      <h1>PDF Q&amp;A (offline RAG)</h1>
      <p className="pdfqa-hint">
        Requires Ollama running locally (<code>ollama pull mistral</code>) and ffmpeg on PATH for voice.
        Set <code>VOSK_MODEL_PATH</code> on the server to use Vosk instead of Whisper.
      </p>

      <section className="pdfqa-card">
        <label className="pdfqa-upload">
          <Upload size={18} />
          <span>{uploading ? "Uploading…" : "Upload PDF"}</span>
          <input type="file" accept=".pdf,application/pdf" hidden onChange={onUpload} disabled={uploading} />
        </label>
        {documentId && <p className="pdfqa-meta">Document ID: {documentId}</p>}
      </section>

      <section className="pdfqa-card">
        <textarea
          className="pdfqa-input"
          rows={3}
          placeholder="Type your question…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <div className="pdfqa-actions">
          <button type="button" className="pdfqa-btn" disabled={asking} onClick={() => ask()}>
            <Send size={16} /> Ask
          </button>
          {!recording ? (
            <button type="button" className="pdfqa-btn pdfqa-btn-mic" onClick={startRec} disabled={asking}>
              <Mic size={16} /> Voice
            </button>
          ) : (
            <button type="button" className="pdfqa-btn pdfqa-btn-stop" onClick={stopRec}>
              <Square size={16} /> Stop
            </button>
          )}
        </div>
      </section>

      {answer && (
        <section className="pdfqa-card">
          <h2>Answer</h2>
          <pre className="pdfqa-answer">{answer}</pre>
          {audioUrl && (
            <audio className="pdfqa-audio" controls src={audioUrl} />
          )}
        </section>
      )}
    </div>
  );
}
