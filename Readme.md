# Wavoscope – musician-oriented audio transcription workbench

Wavoscope is a tool designed to assist musicians in transcribing audio by providing high-quality playback, waveform visualization, and precise flagging/labeling of musical events.

> **Note to Contributors & Agents:** Please refer to [AGENTS.md](AGENTS.md) for current project goals and development guidance.

## Project Status: Web Migration Complete
Wavoscope has successfully migrated from a legacy PySide6 (Qt) interface to a modern, browser-based React architecture. This change reduces distribution size, improves UI flexibility, and enhances portability across operating systems.

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js and npm

### Quick Start
To build and launch Wavoscope Web:

1. **Build the app:**
   - **Windows:** Run `build_app.bat`
   - **Linux/macOS:** Run `./build_app.sh`

2. **Run the app:**
   - **Windows:** Run `run_web.bat`
   - **Linux/macOS:** Run `./run_web.sh`

This will start the FastAPI server on port 8000 and the React development server on port 3000, then open your browser to `http://localhost:3000`.

### Manual Setup
1. **Backend:**
   ```bash
   pip install -r requirements.txt
   python -m wavoscope
   ```
2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev -- --port 3000
   ```

---

## Architecture
- **Backend:** FastAPI (Python) handles audio processing, project management, and state via WebSockets.
- **Frontend:** React (Vite) provides a high-performance interface with `<canvas>`-based visualization.
- **Audio Engine:** Uses `sounddevice` and `numpy` for efficient, framework-independent playback.
