# Project Structure

This document outlines the directory structure and the purpose of each component in the Wavoscope repository.

## Directory Overview

-   **`audio/`**: Contains the core audio engine.
    -   `audio_backend.py`: The main audio playback engine, handling file I/O, speed control, and real-time streams.
    -   `ringbuffer.py`: Implementation of a lock-free ring buffer for audio data.
    -   `spectrum_analyzer.py`: Logic for computing FFTs and spectral data.
    -   `synth.py`: Simple synthesis for metronome clicks.
    -   `waveform_cache.py`: Manages the generation and caching of waveform data for efficient display.
-   **`cli/`**: Contains command-line interface utilities.
    -   `flag_cli.py`: Utilities for managing flags via the terminal.
-   **`config/`**: Configuration files and default settings for the application.
-   **`docs/`**: Project documentation, including task roadmaps and structure guides.
-   **`frontend/`**: The React graphical user interface.
-   `src/App.tsx`: The primary application component.
-   `src/store.ts`: State management using zustand.
-   **`backend/`**: FastAPI backend server.
-   `main.py`: Endpoints for audio control and data retrieval.
-   **`resources/`**: Static assets like icons (SVG) and application resources.
-   **`session/`**: Handles project persistence and high-level state.
    -   `project.py`: The `Project` class which ties audio, metadata (flags), and caching together.
    -   `schema.json`: JSON schema for the `.oscope` sidecar files.
-   **`utils/`**: General helper functions and shared utilities.
    -   `config.py`: Configuration loading/saving logic.

## Root Files

-   **`main.py`**: The entry point for the application, launching the backend and pywebview.
-   **`AGENTS.md`**: Guidance and roadmap for AI agents working on the project.
-   **`Readme.md`**: General project overview and setup instructions.
-   **`requirements.txt`**: Python dependencies.
-   **`Wavoscope.spec`**: PyInstaller specification file for building the executable.
