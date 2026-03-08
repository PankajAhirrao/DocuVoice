import "./Sidebar.css";
import { Link } from "react-router-dom";
import { LayoutDashboard, Upload, Library, History, Settings } from "lucide-react";

export default function Sidebar() {

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>
          DocuVoice <span>AI</span>
        </h2>
      </div>

      <div className="sidebar-menu">
        <Link className="sidebar-item" to="/">
          <LayoutDashboard size={18} />
          Dashboard
        </Link>

        <Link className="sidebar-item" to="/">
          <Upload size={18} />
          Upload Paper
        </Link>

        <Link className="sidebar-item" to="/">
          <Library size={18} />
          Paper Library
        </Link>

        <Link className="sidebar-item" to="/">
          <History size={18} />
          Analysis History
        </Link>

        <Link className="sidebar-item" to="/settings">
          <Settings size={18} />
          Settings
        </Link>
      </div>

    </div>
  );
}