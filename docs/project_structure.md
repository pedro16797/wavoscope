# Project Structure

This document outlines the directory structure and the purpose of each component in the Wavoscope repository.

## Directory Overview

-   **`audio/`**: Contains the core audio engine.
    -   `audio_backend.py`: The main audio playback engine, handling file I/O, speed control, and real-time streams.
    -   `ringbuffer.py`: Implementation of a lock-free ring buffer for audio data.
    -   `spectrum_analyzer.py`: Logic for computing FFTs and spectral data.
    -   `synth.py`: Simple synthesis for metronome clicks.
    -   `waveform_cache.py`: Manages the generation and caching of waveform data for efficient display.
-   **`backend/`**: The modern FastAPI-based web backend.
    -   `main.py`: Entry point for the FastAPI server, serving API endpoints and frontend assets.
-   **`cli/`**: Contains command-line interface utilities.
    -   `flag_cli.py`: Utilities for managing flags via the terminal.
-   **`config/`**: Configuration files and default settings for the application.
-   **`docs/`**: Project documentation, including task roadmaps and structure guides.
-   **`frontend/`**: The React-based graphical user interface.
    -   `src/components/`: React components (Waveform, Spectrum, Timeline, PlaybackBar).
    -   `src/store/`: Frontend state management (Zustand).
    -   `dist/`: Built production assets.
-   **`resources/`**: Static assets like icons (SVG), themes (JSON), and application resources.
-   **`session/`**: Handles project persistence and high-level state.
    -   `project.py`: The `Project` class which ties audio, metadata (flags), and caching together.
-   **`utils/`**: General helper functions and shared utilities.

## Root Files

-   **`run.sh` / `run.bat`**: Scripts to set up the environment and launch the application.
-   **`build.sh` / `build.bat`**: Scripts to build the frontend and package the application.
-   **`main.py`**: The entry point for the application. Now launches FastAPI + pywebview.
-   **`AGENTS.md`**: Guidance and roadmap for AI agents working on the project.
-   **`Readme.md`**: General project overview and setup instructions.
-   **`requirements.txt`**: Python dependencies.
