# Wavoscope – musician-oriented audio transcription workbench

Wavoscope is a tool designed to assist musicians in transcribing audio by providing high-quality playback, waveform visualization, and precise flagging/labeling of musical events.

> **Note to Contributors & Agents:** Please refer to [AGENTS.md](AGENTS.md) for current project goals and development guidance.

## Project Status: GUI Migration Complete
The graphical user interface has been migrated from PySide6 (Qt) to a modern, browser-based architecture using React and FastAPI.

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js & npm (for frontend development)

### Installation
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```
2. Build the frontend:
```bash
cd frontend && npm install && npm run build && cd ..
```

### Run the app
```bash
python main.py
```

### Build (Standalone)
To create a standalone executable using Nuitka:
```bash
python -m nuitka --standalone --include-package-data=audio,session,utils,backend --include-data-dir=resources=resources --include-data-dir=config=config --include-data-dir=frontend/dist=frontend/dist --output-dir=dist-nuitka main.py
```
