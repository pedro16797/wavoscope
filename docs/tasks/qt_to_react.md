# Task: Replace Qt with React

## Objective
Migrate the Wavoscope GUI from PySide6 (Qt) to a browser-based interface using React for the frontend and a Python backend (FastAPI).

## Rationale
-   **Reduce Distribution Size:** Removing large Qt libraries (PySide6) significantly reduces the final binary size (from ~150MB to <50MB).
-   **Modern UI Flexibility:** Leverage the React ecosystem for better look & feel, easier styling, and responsive design.
-   **Cross-Platform Consistency:** Browsers provide a more consistent rendering environment across OSs compared to Qt's native widgets.
-   **Maintainability:** Component-based architecture and modern state management (Zustand) simplify complex UI logic.

## Critical Analysis & Decisions

### Qt Functionality Audit
The current implementation performs the following functionalities that must be ported for parity:
1.  **Layout & Window Management:**
    *   [x] Main window with vertical layout.
    *   [x] Resizable vertical splitter between waveform and spectrum areas.
    *   [x] System menu bar (File: Open, Save, Exit) - *Implemented using pywebview native menu.*
    *   [x] Unsaved changes confirmation dialog - *Implemented using pywebview confirmation.*
2.  **Audio Visualization:**
    *   [x] **Waveform View:** Scrollable and zoomable canvas-based drawing of audio bars. Adaptive rendering based on zoom level.
    *   [x] **Spectrogram View:** FFT-based visualization with frequency range mapping and a piano roll overlay for pitch reference.
    *   [x] **Timeline:** Time-ruler with grid lines, time labels, and flag markers.
3.  **Playback Controls:**
    *   [x] Buttons for Play, Pause, and Stop (returns to the last play start position).
    *   [x] Volume and playback speed (0.1x to 4.0x) sliders.
    *   [x] Metronome toggle and click volume control.
    *   [x] FFT window size selection for the spectrogram.
    *   [x] Octave shift for the spectrogram piano roll.
4.  **Transcription Engine (Flags):**
    *   [x] Add flags via click on timeline or keyboard shortcut.
    *   [x] Drag flags to move them (with snapping to a 10ms grid).
    *   [x] Right-click context menu / Dialog for editing flag details (name, subdivision, section start, shading).
    *   [ ] Equi-spaced flag insertion between two existing flags.
    *   [x] Automatic naming of flags (e.g., "1.1", "1.2").
5.  **Project Management:**
    *   [x] Native file selection dialog for opening audio files.
    *   [x] Saving and loading project state (flags, subdivisions, etc.).
6.  **Theming:**
    *   [x] Global theme support with 10+ presets (Dark, Cosmic, Neon, etc.) loaded from JSON.
7.  **Keyboard Interactions:**
    *   [x] Comprehensive keybinds (Space for play/pause, Arrows for seek/speed, Ctrl+S for save, etc.).
    *   [x] Repeat-key handling for smooth seeking and speed adjustment.

### Questions & Answers
- **Does React support all the functionalities we need for parity?**
  Yes. `<canvas>` or WebGL provides high-performance drawing for waveforms and spectrograms. Libraries like `react-resizable-panels` handle layouts. Modern UI libraries (Radix UI, Headless UI) handle complex components like menus and dialogs.
- **Does React result in a more compact product?**
  Yes. By using a lightweight webview (like `pywebview`) which leverages the system's native browser engine, we avoid the ~100MB+ overhead of PySide6/Qt libraries and the ~50MB+ overhead of Chromium (Electron).
- **Does React allow for a better looking and more maintainable GUI?**
  Yes. CSS variables and Tailwind/Styled-components make modern, responsive styling trivial compared to QSS. React's declarative state-driven UI is much easier to reason about for complex interactive applications.
- **Are there any alternatives?**
  *   **Electron:** Mature but heavy (large binary size and high RAM usage).
  *   **Tauri:** Great binary size, but requires Rust for the backend or complex bridging to Python.
  *   **Dear ImGui:** Fast and lightweight, but styling is difficult and it's not well-suited for a modern "web-like" UX.
  **Decision:** **React + FastAPI + pywebview** is the optimal choice. It keeps the core logic in Python while providing a modern, compact, and flexible UI.

## Sub-Tasks

### 1. Backend Setup
-   [x] Initialize a FastAPI project in `backend/`.
-   [x] Set up a WebSocket or Server-Sent Events (SSE) for real-time playback position updates.
-   [x] Refactor `AudioBackend` and `Project` to remove `QObject` and `Signal` dependencies.
-   [x] Implement API endpoints for:
    *   `GET /audio/data`: Get waveform/spectrum data.
    *   `POST /playback/control`: Play, pause, seek, set speed/volume.
    *   `GET/POST /project`: Load/save project state.
    *   `GET /browse`: Open native file dialog and return path.

### 2. Frontend Setup
-   [x] Initialize a React project using Vite in `frontend/`.
-   [x] Set up Zustand for global state management (playback status, project data, themes).
-   [x] Implement a Theme Provider that maps our existing JSON themes to CSS variables.

### 3. Core UI Components
-   [x] **Waveform Viewer:** Implement using `<canvas>` with zoom/pan logic parity.
-   [x] **Spectrum Viewer:** Implement spectrogram with piano roll overlay.
-   [x] **Timeline:** Ruler with flag interaction and subdivision rendering.
-   [x] **Playback Bar:** Full set of controls (buttons, sliders, selectors).

### 4. Integration & Optimization
-   [x] Sync playback cursor between backend and frontend with low latency.
-   [x] Implement "Native-like" features: Menus, shortcuts, and "Unsaved Changes" dialog using web tech.
-   [x] Bundle the application using `pywebview` and Nuitka/PyInstaller.

## Remaining Issues & Polish (Next Steps)

1.  **Flag Context Menu Parity:**
    - [x] Right-clicking a flag opens the `FlagDialog`.
    - [x] The dialog includes: Name, Time, Subdivision, Section Start toggle, and "Shade 8th notes" toggle.
    - [x] Add "Delete" as a clear option in the dialog.
    - [ ] *Improvement:* Use a floating context menu (Edit, Delete) before opening the full modal dialog to better match the Qt UX.

2.  **Settings Panel Accessibility:**
    - [ ] Ensure the Settings dialog is easily accessible (e.g., via a dedicated gear icon in the Playback Bar).
    - [ ] Verify all tabs: Global (Theme, Click Volume, Visible Keys) and Keybinds.

3.  **UI Cleanup:**
    - [ ] Remove redundant "Open Audio" button in the Playback Bar; rely on the native `File > Open` menu.
    - [ ] Replace FFT window size dropdown with a bandwidth slider for finer control.

4.  **Legacy Cleanup:**
    - [ ] Once functional parity is 100% verified, remove the legacy `gui/` directory and Qt-related resource files (`resources.qrc`, etc.).
