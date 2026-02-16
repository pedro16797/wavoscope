# Task: Bugs and Performance Improvements

## Objective
General maintenance, bug fixing, and performance optimization to ensure a smooth and reliable user experience.

## Ongoing Items

### 1. Performance Optimization
-   [ ] **Waveform Rendering**: Further optimize the `WaveformCache` to handle extremely long audio files without UI lag.
-   [ ] **Spectrum FFT**: Optimize FFT calculations for higher resolution without increased CPU load.
-   [ ] **Frontend Virtualization**: Ensure large numbers of flags or markers are rendered efficiently using virtualization if necessary.

### 2. Bug Fixes
-   [ ] **Audio Buffer Underruns**: Investigate and fix occasional pops or clicks during high CPU load (e.g., when resizing panels).
-   [ ] **State Synchronization**: Ensure the backend `dirty` state and frontend Save button are always in sync.
-   [ ] **Window Resize**: Fix edge cases where canvases might not resize correctly on certain high-DPI displays.

### 3. Code Quality
-   [ ] **Test Coverage**: Increase unit test coverage for both backend (pytest) and frontend (Vitest).
-   [ ] **Typing**: Ensure strict typing across the codebase (Python type hints and TypeScript).

## Specific Known Issues
-   *None currently reported. Use this section to document bugs as they are discovered.*
