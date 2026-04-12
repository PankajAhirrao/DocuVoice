import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./DocumentHistory.css";
import { API } from "../../api.js";

function displayFileName(name) {
  if (!name) return "Untitled";
  const parts = name.split("_");
  if (parts.length >= 3) return parts.slice(2).join("_");
  return name;
}

export default function DocumentHistory() {
  const authToken = localStorage.getItem("authToken");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!authToken) {
      setLoading(false);
      return;
    }
    axios
      .get(`${API}/users/history/`, {
        headers: { Authorization: `Token ${authToken}` },
      })
      .then((res) => setHistory(res.data.file_history || []))
      .catch(() => setHistory([]))
      .finally(() => setLoading(false));
  }, [authToken]);

  const handleView = (file) => {
    navigate(`/viewer/${file.id}`, { state: null });
  };

  return (
    <div className="history-card">
      <div className="card-header">
        <h2 className="card-title">Recent Papers</h2>
        <p className="card-description">
          Your latest uploads and analyses will appear here.
        </p>
      </div>

      <div className="card-content">
        {loading ? (
          <div className="history-loading">Loading history…</div>
        ) : history.length === 0 ? (
          <div className="history-empty">No papers analyzed yet. Upload a paper to get started.</div>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>Paper</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {history.map((file) => (
                <tr key={file.id}>
                  <td>{displayFileName(file.file_name)}</td>
                  <td>{file.uploaded_at}</td>
                  <td>
                    <button
                      type="button"
                      className="view-btn"
                      onClick={() => handleView(file)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
