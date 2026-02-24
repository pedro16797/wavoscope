# Project Structure

This document outlines the directory structure and the purpose of each component in the Wavoscope repository.

## Directory Overview

-   **`audio/`**: Contains the core audio engine.
    -   `audio_backend.py`: The main audio backend facade.
    -   `chord_analyzer.py`: Chroma-based chord detection for chord flags.
    -   `ringbuffer.py`: Thread-safe ring buffer for audio streaming.
    -   `spectrum_analyzer.py`: Logic for computing FFTs and spectral data.
    -   `synth.py`: Real-time synthesis for metronome clicks and chord auditioning.
    -   `waveform_cache.py`: Manages the generation and caching of waveform data for efficient display.
    -   **`engine/`**: Low-level audio processing components.
        -   `playback.py`: Core playback logic and stream management.
        -   `processing.py`: Audio stretching (TSM) and buffer management.
        -   `metronome.py`: Metronome click timing and generation.
        -   `filters.py`: Real-time biquad filtering (band-pass).
-   **`backend/`**: The modern FastAPI-based web backend.
    -   `main.py`: Entry point for the FastAPI server, serving API endpoints and frontend assets.
    -   `state.py`: Shared global state (the active `Project` instance).
    -   `routers/`: Modular FastAPI routers for different API domains (audio, playback, project, etc.).
-   **`cli/`**: Contains command-line interface utilities.
    -   `flag_cli.py`: Utilities for managing flags via the terminal.
-   **`config/`**: Configuration files and default settings for the application.
-   **`docs/`**: Project documentation, including task roadmaps and structure guides.
-   **`frontend/`**: The React-based graphical user interface.
    -   `src/components/`: React components (Waveform, Spectrum, Timeline, PlaybackBar).
    -   `src/store/`: Frontend state management (Zustand).
    -   `dist/`: Built production assets.
-   **`resources/`**: Static assets like icons (SVG), themes (JSON), and application resources.
-   **`scripts/`**: Automation and utility scripts (e.g., screenshot generation).
-   **`session/`**: Handles project persistence and high-level state.
    -   `project.py`: The `Project` class which ties audio, metadata (flags), and caching together.
    -   `manager.py`: Handles `.oscope` sidecar file I/O and scrubbing.
    -   `flags.py`: Manages rhythm and chord flag lists.
    -   `looping.py`: Logic for various loop modes (all, section, marker, lyric).
    -   `export.py`: MusicXML export generation.
    -   `chord_utils.py`: Helpers for chord name parsing and validation.
-   **`utils/`**: General helper functions and shared utilities.

## Root Files

-   **`run.sh` / `run.bat`**: Scripts to set up the environment and launch the application.
-   **`main.py`**: The entry point for the application. Now launches FastAPI + pywebview.
-   **`AGENTS.md`**: Guidance and roadmap for AI agents working on the project.
-   **`Readme.md`**: General project overview and setup instructions.
-   **`LICENSE`**: The project's MIT license terms.
-   **`SECURITY.md`**: Policy for reporting security vulnerabilities.
-   **`requirements.txt`**: Python dependencies.
