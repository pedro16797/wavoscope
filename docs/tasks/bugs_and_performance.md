# Task: Bugs and Performance Improvements

## Objective
Conduct a thorough audit of the Wavoscope codebase to identify and fix bugs, and optimize performance for a smoother user experience.

## Sub-Tasks

### 1. Static Analysis & Code Quality
-   [ ] Run static analysis tools (e.g., `ruff`, `pylint`, `mypy`) to identify potential bugs and code quality issues.
-   [ ] Refactor complex methods and improve docstring coverage.
-   [ ] Ensure consistent naming conventions and code style across the project.

### 2. Performance Profiling
-   [ ] Use `cProfile` or `pyinstrument` to profile the application, especially during:
    -   Audio file loading and waveform cache generation.
    -   Real-time playback and GUI updates.
    -   Spectrum analysis.
-   [ ] Identify and eliminate bottlenecks in `AudioBackend._audio_callback`.

### 3. Memory Audit
-   [ ] Audit memory usage, particularly in `WaveformCache`.
-   [ ] Check for memory leaks in long-running sessions.
-   [ ] Optimize the storage of waveform data for very long audio files.

### 4. Threading & Concurrency
-   [ ] Review the interaction between the audio thread and the main thread to prevent race conditions or deadlocks.
-   [ ] Ensure that all UI updates are performed safely (especially during the migration to a web-based architecture).

### 5. Bug Hunting
-   [ ] Test edge cases such as very short/long audio files, unsupported formats, and rapid user interactions.
-   [ ] Verify the accuracy of the metronome clicks and flag positioning.
-   [ ] Fix any identified issues with project saving/loading (oscope sidecar files).
