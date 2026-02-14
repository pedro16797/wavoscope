# Wavoscope – musician-oriented audio transcription workbench

Wavoscope is a tool designed to assist musicians in transcribing audio by providing high-quality playback, waveform visualization, and precise flagging/labeling of musical events.

> **Note to Contributors & Agents:** Please refer to [AGENTS.md](AGENTS.md) for current project goals and development guidance.

## Architecture
Wavoscope uses a modern, browser-based React architecture for the frontend and a Python FastAPI backend. This provides a lightweight distribution (<50MB) and a highly responsive, flexible user interface.

---

## Getting Started

### Run the app
The easiest way to run Wavoscope is using the provided scripts, which handle virtual environment setup and dependencies automatically:

**Windows:**
```batch
run.bat
```

**Linux/macOS:**
```bash
./run.sh
```

### Build
To create a standalone executable:

**Windows:**
```batch
build.bat
```

**Linux/macOS:**
```bash
./build.sh
```

### Manual Development Setup
1. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. **Backend:**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
