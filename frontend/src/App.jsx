import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard/Dashboard";
import DocumentViewer from "./pages/DocumentViewer/DocumentViewer";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import NotFound from "./pages/NotFound/NotFound";

import Navbar from "./component/Navbar/Navbar";
import Sidebar from "./component/Sidebar/Sidebar";
import "./App.css";

function App() {
  return (
    <Router>
      <Navbar />

      <div className="app-shell">
        <div className="app-body">
          <aside className="app-sidebar">
            <Sidebar />
          </aside>
          <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/viewer/:id" element={<DocumentViewer />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;