# Wavoscope – musician-oriented audio transcription workbench

Wavoscope is a tool designed to assist musicians in transcribing audio by providing high-quality playback, waveform visualization, and precise flagging/labeling of musical events.

> **Note to Contributors & Agents:** Please refer to [AGENTS.md](AGENTS.md) for current project goals and development guidance.

## Project Status: GUI Migration
We are currently in the process of migrating the graphical user interface from PySide6 (Qt) to a modern, browser-based React architecture. This change aims to reduce distribution size and improve UI flexibility.

---

## New (Web-based) Implementation

### Prerequisites
- Python 3.10+
- Node.js and npm

### Quick Start
To launch both the backend and frontend:
- **Windows:** Run `run_web.bat`
- **Linux/macOS:** Run `./run_web.sh`

This will start the FastAPI server on port 8000 and the React development server on port 3000, then open your browser to `http://localhost:3000`.

### Manual Setup
1. **Backend:**
   ```bash
   pip install -r requirements.txt fastapi uvicorn
   python backend/main.py
   ```
2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev -- --port 3000
   ```

---

## Legacy (Qt-based) Implementation

### Run the app
```bash
python -m wavoscope 
```

### Get requirements
```bash
pip install -r requirements.txt
```

### Build
To create a standalone executable using Nuitka:
```bash
python -m nuitka --standalone --enable-plugin=pyside6 --include-package-data=wavoscope --include-qt-plugins=sensible,styles,imageformats --include-data-dir=resources=resources --noinclude-data-files="**/.git/**" --noinclude-data-files="**/venv/**" --noinclude-data-files="**/__pycache__/**" --noinclude-data-files="**/requirements.txt" --noinclude-data-files="**/Wavoscope.spec" --noinclude-data-files="**/README.md" --nofollow-import-to=pytest --windows-icon-from-ico=resources/icons/app-icon.png --output-dir=dist-nuitka --assume-yes-for-downloads --jobs=0 main.py
```
