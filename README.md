# SpecSense AI — Intelligent Cable Specification & Inspection Control System

**SpecSense AI** is a state-of-the-art computer vision and natural language processing system built to automate cable specification extraction, datasheet analysis, and structural cross-section inspection.

The system features two user interfaces:
1. **React & FastAPI Enterprise Portal (Recommended)**: A high-fidelity, dual-server application with real-time dashboards, persistent inspection logs (using PostgreSQL with transparent SQLite fallback), interactive design calculation sheets, and robust proxy routing.
2. **Streamlit Quick Console**: A lightweight, single-page python interface for rapid local testing and single-spec parsing.

---

## 🚀 Key Modules & Capabilities

* **Vision Cable Inspection (YOLOv8)**: Run cross-section segmentations and classification on cable images to compute structural measurements (diameters, layers, insulation status).
* **Technical Datasheet Parser (OCR & Spacy)**: Extract and clean key attributes (Voltage, Current, Armour, Shielding) from PDF datasheets.
* **Intelligent Wiring & Feeder Designer**: Enter power requirements, distances, and voltage parameters to automatically calculate wiring gauges, circuit designs, and voltage drops.
* **History Feed & Analytics**: Access a central operational log of past analyses, vision runs, and design projects.

---

## 📂 Project Structure

```text
SpecSense AI/
├── SpecSense_AI_React/       # React & FastAPI Enterprise Workspace
│   ├── artifacts/frontend/   # React Single Page App (Vite + TS + Custom Glassmorphism CSS)
│   ├── server.py             # FastAPI Backend Server (Uvicorn)
│   ├── db_manager.py         # DB Manager with PostgreSQL to SQLite Fallback
│   └── run_project.bat       # Startup script for both React & FastAPI servers
│
├── SpecSense.bat             # Streamlit quick console startup script
├── app.py                    # Streamlit application entry point
│
├── Vision_Model/             # Core YOLO v8 training & inference pipelines
├── OCR_Reader/               # OCR text extraction algorithms
├── Keyword_Generator/        # Product keyword generation logic
└── Validator/                # Engineering standards compliance validator
```

---

## 🛠️ Quick Start

### Method 1: React & FastAPI Enterprise Workspace (Recommended)

To run the full React client and FastAPI server:
1. Navigate to the `SpecSense_AI_React/` directory.
2. Configure your API credentials inside `.env` (copy from `.env.example`).
3. Double-click the **`run_project.bat`** script or run it from your command prompt:
   ```cmd
   cd SpecSense_AI_React
   run_project.bat
   ```
This script automatically:
* Safely terminates any dangling/zombie processes on ports `8000` (FastAPI) and `5173` (Vite) using robust PowerShell bindings.
* Boots the Uvicorn FastAPI server on `http://127.0.0.1:8000`.
* Boots the Vite React application on `http://localhost:5173`.
* Polls the backend until it is fully active (handling PostgreSQL connection timeouts and SQLite fallback transparently), then opens the browser automatically.

---

### Method 2: Streamlit Quick Console

To run the lightweight Streamlit application:
1. Double-click the **`SpecSense.bat`** script in the project root:
   ```cmd
   SpecSense.bat
   ```
This will configure your virtual environment, install requirements, and boot Streamlit at `http://localhost:8501`.

---

## 📦 Database Modes

The React interface features robust dual-database operation:
* **PostgreSQL (Production)**: Connects to your Postgres server defined in `.env` for multi-user deployments.
* **SQLite (Fallback)**: If PostgreSQL is offline, the backend automatically falls back to `specsense_local.db` in the background. No manual setup or Docker is required to start developing immediately.
