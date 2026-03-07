# DocuVoice AI — IEEE Research Paper Analyzer

## Overview

**DocuVoice AI** is an AI-powered platform for **analyzing IEEE research papers**. It helps researchers and students upload papers, extract text, analyze specific sections, and get AI-generated summaries, key contributions, technical keywords, Q&A, and citations—all through a modern web interface.

The project combines:

- **React (Vite)** frontend — modern, responsive UI
- **Django** backend — API, text extraction, and AI analysis
- **Section-based analysis** — choose which part of the paper to analyze (Abstract, Methodology, Results, etc.)

---

## Features

### Upload & Section Analysis

- Upload **IEEE research papers** in **PDF** or **DOCX**
- **Section selector**: analyze the full paper or a specific section:
  - Full Paper · Title · Abstract · Introduction · Related Work
  - Methodology · Dataset / Experimental Setup · Results
  - Discussion · Conclusion · References · Citations · Figures & Tables

### AI Analysis Panel

- **Summary** — concise overview of the paper or selected section
- **Key Contributions** — main findings and contributions
- **Technical Keywords** — important terms and concepts
- **Generated Questions** — Q&A to deepen understanding
- **Methodology Insights** — experimental setup and approach
- **Citations Extracted** — references and citations
- **Read Aloud** — listen to the summary or extracted text

### Dashboard & Navigation

- **Dashboard** — stats (Papers Analyzed, AI Insights Generated, Time Saved), upload card, and recent papers
- **Sidebar** — Dashboard, Upload Paper, Paper Library, Analysis History, Settings
- **Document Viewer** — two-column layout: PDF viewer (left) and AI analysis tabs (right)

### Modern UI

- Clean layout: **Navbar** (top) · **Sidebar** (left) · **Main content** (right)
- Card-based design, consistent spacing, and modern typography (Inter)
- Responsive layout for desktop, tablet, and mobile

---

## Project Structure

```
DocuVoice/
├── backend/          → Django API, text extraction, AI/analysis logic
├── frontend/         → React (Vite) UI
│   ├── src/
│   │   ├── component/   → Navbar, Sidebar, UploadDocument, Stats, DocumentHistory, etc.
│   │   ├── pages/       → Dashboard, DocumentViewer, Login, Register, Index
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/PankajAhirrao/DocuVoice.git
cd DocuVoice
```

### 2. Backend (Django)

```bash
cd backend

# Optional: create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Linux / macOS

# Install dependencies
pip install -r requirements.txt

# Run migrations (if applicable)
python manage.py migrate

# Start the backend server
python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000**

### 3. Frontend (React + Vite)

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

### 4. Environment (optional)

Create a `.env` file in `frontend` (or set `VITE_API_URL`) so the frontend points to your Django API, for example:

```env
VITE_API_URL=http://127.0.0.1:8000/
```

---

## How It Works

1. **Upload** — User uploads an IEEE paper (PDF/DOCX) and selects a section to analyze.
2. **Backend** — Django receives the file and section, extracts text, and runs analysis (summarization, keywords, Q&A, citations, etc.).
3. **Viewer** — User is taken to the Document Viewer: left side shows the PDF (or file info), right side shows tabs (Summary, Key Contributions, Technical Keywords, Generated Questions, Methodology Insights, Citations, Read Aloud).
4. **Dashboard** — Stats and recent papers are shown on the main dashboard; navigation is via the sidebar.

---

## Tech Stack

| Layer    | Technology        |
| -------- | ----------------- |
| Frontend | React 18, Vite   |
| UI       | CSS, modern layout (flexbox/grid) |
| Backend  | Django, Django REST (or similar) |
| API      | REST; file upload + section parameter |

---

## License

This project is part of the DocuVoice repository. See the repository for license details.

---

## Contributing

1. Fork the repository  
2. Create a feature branch  
3. Commit your changes  
4. Push to the branch and open a Pull Request  

For bugs or feature requests, please open an issue on [GitHub](https://github.com/PankajAhirrao/DocuVoice).
