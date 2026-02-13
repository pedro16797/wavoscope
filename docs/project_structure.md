# Project Structure

This document outlines the directory structure and the purpose of each component in the Wavoscope repository.

## Directory Overview

-   **`audio/`**: Contains the core audio engine (Qt-free).
    -   `audio_backend.py`: The main audio playback engine, handling file I/O, speed control, and real-time streams.
    -   `ringbuffer.py`: Implementation of a lock-free ring buffer for audio data.
    -   `spectrum_analyzer.py`: Logic for computing FFTs and spectral data.
    -   `synth.py`: Simple synthesis for metronome clicks.
    -   `waveform_cache.py`: Manages the generation and caching of waveform data for efficient display.
-   **`backend/`**: Contains the FastAPI backend for the web-based GUI.
    -   `main.py`: Entry point for the FastAPI server.
-   **`cli/`**: Contains command-line interface utilities.
    -   `flag_cli.py`: Utilities for managing flags via the terminal.
-   **`config/`**: Configuration files and default settings for the application.
-   **`docs/`**: Project documentation, including task roadmaps and structure guides.
-   **`frontend/`**: The modern React-based graphical user interface (Vite).
-   **`resources/`**: Static assets like icons (SVG).
-   **`session/`**: Handles project persistence and high-level state (Qt-free).
    -   `project.py`: The `Project` class which ties audio, metadata (flags), and caching together.
    -   `schema.json`: JSON schema for the `.oscope` sidecar files.
-   **`utils/`**: General helper functions and shared utilities.
    -   `config.py`: Configuration loading/saving logic.
    -   `keybind_manager.py`: Handles keyboard shortcut mapping.

## Root Files

-   **`__main__.py`**: The primary entry point for launching the FastAPI server.
-   **`AGENTS.md`**: Guidance and roadmap for AI agents working on the project.
-   **`Readme.md`**: General project overview and setup instructions.
-   **`requirements.txt`**: Python dependencies.
-   **`build_app.sh` / `build_app.bat`**: Unified scripts for building the frontend and setting up the environment.
-   **`run_web.sh` / `run_web.bat`**: Scripts for launching both backend and frontend servers.
