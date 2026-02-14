# Wavoscope – musician-oriented audio transcription workbench

Wavoscope is a tool designed to assist musicians in transcribing audio by providing high-quality playback, waveform visualization, and precise flagging/labeling of musical events.

> **Note to Contributors & Agents:** Please refer to [AGENTS.md](AGENTS.md) for current project goals and development guidance.

## Project Status: GUI Migration
We are currently in the process of migrating the graphical user interface from PySide6 (Qt) to a modern, browser-based React architecture. This change aims to reduce distribution size and improve UI flexibility.

---

## Modern (React + FastAPI) Implementation

### Development
1. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. **Backend:**
   ```bash
   python main.py
   ```

### Get requirements
```bash
pip install -r requirements.txt
pip install fastapi uvicorn websockets pywebview
```

### Build
To create a standalone executable using Nuitka (without Qt overhead):
```bash
python -m nuitka --standalone --include-package-data=wavoscope --include-data-dir=frontend/dist=frontend/dist --include-data-dir=resources=resources --noinclude-data-files="**/.git/**" --noinclude-data-files="**/venv/**" --noinclude-data-files="**/__pycache__/**" --windows-icon-from-ico=resources/icons/app-icon.png --output-dir=dist main.py
```
