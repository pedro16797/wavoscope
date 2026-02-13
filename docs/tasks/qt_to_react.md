# Task: Replace Qt with React

## Objective
Migrate the Wavoscope GUI from PySide6 (Qt) to a browser-based interface using React for the frontend and a Python backend (FastAPI recommended).

## Rationale
-   Reduce the distribution size by removing large Qt libraries.
-   Improve UI flexibility and leverage the modern React ecosystem.
-   Better portability across different operating systems.

## Sub-Tasks

### 1. Backend Setup
-   [x] Initialize a FastAPI or Flask project.
-   [x] Set up a WebSocket or REST API to handle communication between the frontend and backend.
-   [x] Port the `AudioBackend` and `Project` logic from `audio/` and `session/`.
    -   *Note:* Remove Qt-specific dependencies like `QObject` and `Signal` from these core classes.
-   [x] Implement endpoints for:
    -   [x] Loading audio files.
    -   [x] Playback control (play, pause, seek, set speed).
    -   [x] Managing flags (add, remove, move, list).
    -   [x] Retrieving waveform and spectrum data.

### 2. Frontend Setup
-   [x] Initialize a React project (e.g., using Vite) in a `frontend/` directory.
-   [x] Set up a state management system (e.g., Redux, Zustand, or simple React Context).
-   [x] Implement a communication layer to talk to the Python backend.

### 3. Core UI Components
-   [x] **Waveform Viewer:** Implement a high-performance waveform viewer. Use `<canvas>` or WebGL to handle large audio files smoothly.
-   [x] **Spectrum Viewer:** Implement the spectrogram view.
-   [x] **Timeline & Playback Bar:** Create a timeline that tracks the current playback position.
-   [x] **Flag/Label Management:** Implement a UI for adding and editing transcription flags.
-   [x] **Controls:** Implement play/pause buttons, speed slider, and volume control.

### 4. Integration & Optimization
-   [x] Ensure low-latency synchronization between the audio playback and the UI position.
-   [x] Implement efficient data streaming for waveform and spectrum data.
-   [x] Test the UI on different browsers.

### 5. Packaging & Distribution
-   [x] Determine the best way to bundle the application (e.g., PyInstaller with a bundled web server, or using a lightweight webview like `pywebview`).
-   [x] Update the build process to include the frontend assets.
