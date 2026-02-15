# Task: Bugs and Performance Improvements

## Objective
Conduct a thorough audit of the Wavoscope codebase to identify and fix bugs, and optimize performance for a smoother user experience.

## Sub-Tasks

### 0. Splitting Monolithic Scripts & Code Structure
- [x] Refactor `backend/main.py` into modular routers (e.g., `audio.py`, `project.py`, `config.py`).
- [ ] Modularize frontend state and logic if `App.tsx` or main store becomes too large.
- [x] Ensure consistent, clean, and properly documented code structure across both Python and React codebases.
- [x] Audit and remove any remaining legacy Qt-related code that is no longer used.

### 1. Static Analysis & Code Quality
- [ ] Run static analysis tools for Python (e.g., `ruff`, `mypy`) to identify potential bugs and code quality issues.
- [x] Implement linting and type checking for the React frontend (e.g., `eslint`, `tsc`).
- [x] Refactor complex methods and improve docstring/JSDoc coverage.
- [x] Ensure consistent naming conventions and code style across the project.

### 2. Performance Profiling
- [ ] Use `cProfile` or `pyinstrument` to profile the FastAPI backend, especially during:
  - Audio file loading and waveform cache generation.
  - Spectrum analysis calculation.
- [ ] Profile frontend performance using browser DevTools:
  - Optimize React component re-renders.
  - Profile `<canvas>` rendering performance for waveform and spectrogram.
- [ ] Identify and eliminate bottlenecks in `AudioBackend._audio_callback`.

### 3. Memory Audit
- [ ] Audit memory usage in the backend, particularly in `WaveformCache`.
- [ ] Monitor browser memory usage, ensuring large waveform data arrays are handled efficiently.
- [ ] Check for memory leaks in long-running sessions (both backend and frontend).

### 4. Concurrency & Real-time Sync
- [ ] Review the interaction between the audio thread and the FastAPI event loop.
- [ ] Optimize WebSocket communication for real-time playback position updates to minimize latency and overhead.
- [ ] Ensure thread-safe access to project data in the backend when accessed via multiple API/WS requests.

### 5. Bug Hunting & Testing
- [x] Implement unit tests for core backend logic and API endpoints.
- [ ] Implement frontend tests to ensure UI reliability and correctness.
- [ ] Test edge cases such as very short/long audio files, unsupported formats, and rapid user interactions.
- [ ] Verify the accuracy of the metronome clicks and flag positioning in the web-based UI.
- [x] Fix any identified issues with project saving/loading (oscope sidecar files).
