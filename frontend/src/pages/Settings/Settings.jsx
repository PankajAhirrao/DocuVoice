import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "react-toastify";
import { User, Trash2, LogOut } from "lucide-react";
import "./Settings.css";

export default function Settings() {
  const apiUrl = import.meta.env.VITE_API_URL?.replace(/\/?$/, "/");
  const authToken = localStorage.getItem("authToken");
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [cleaning, setCleaning] = useState(false);
  const navigate = useNavigate();

  const handleCleanup = async () => {
    if (!authToken || !apiUrl) return;
    if (!window.confirm("Delete all your uploaded papers and analysis history? This cannot be undone.")) return;
    setCleaning(true);
    try {
      await axios.delete(`${apiUrl}users/cleanup/`, {
        headers: { Authorization: `Token ${authToken}` },
      });
      toast.success("All files and history have been cleared.");
      window.location.reload();
    } catch (e) {
      toast.error("Failed to clear history: " + (e?.response?.data?.error || e?.message));
    } finally {
      setCleaning(false);
    }
  };

  const handleLogout = () => {
    if (!authToken || !apiUrl) {
      localStorage.removeItem("authToken");
      localStorage.removeItem("user");
      navigate("/login");
      return;
    }
    axios
      .post(`${apiUrl}users/logout/`, {}, { headers: { Authorization: `Token ${authToken}` } })
      .catch(() => {})
      .finally(() => {
        localStorage.removeItem("authToken");
        localStorage.removeItem("user");
        navigate("/login");
      });
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your account and preferences.</p>
      </div>

      <div className="settings-sections">
        <section className="settings-card">
          <h2 className="settings-card-title">
            <User size={20} />
            Account
          </h2>
          <div className="settings-row">
            <span className="settings-label">Username</span>
            <span className="settings-value">{user?.username || "—"}</span>
          </div>
          <div className="settings-row">
            <span className="settings-label">Email</span>
            <span className="settings-value">{user?.email || "—"}</span>
          </div>
        </section>

        <section className="settings-card">
          <h2 className="settings-card-title">
            <Trash2 size={20} />
            Data
          </h2>
          <p className="settings-desc">Clear all uploaded papers and analysis history from your account.</p>
          <button
            type="button"
            className="settings-btn settings-btn-danger"
            onClick={handleCleanup}
            disabled={cleaning}
          >
            {cleaning ? "Clearing…" : "Clear All History"}
          </button>
        </section>

        <section className="settings-card">
          <h2 className="settings-card-title">
            <LogOut size={20} />
            Session
          </h2>
          <button type="button" className="settings-btn" onClick={handleLogout}>
            Log Out
          </button>
        </section>
      </div>
    </div>
  );
}
