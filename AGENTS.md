# Agent Guidance for Wavoscope

Welcome, Agent. This document serves as the primary entry point for understanding the current goals and tasks in the Wavoscope repository.

## Project Overview
Wavoscope is a musician-oriented audio transcription workbench. It is a desktop application built with a React frontend and a FastAPI backend.

## Main Objectives
We are currently focusing on the following initiatives:

1.  **Quality & Performance Audit:** A comprehensive review of the project to identify bugs, optimize performance, and ensure code quality.
    -   Detailed Task: [Bugs and Performance improvements](docs/tasks/bugs_and_performance.md)
2.  **Audio Quality Enhancement (NovaSR):** Studying and integrating the ComfyUI-NovaSR model for audio super-resolution to improve the quality of slowed-down playback.
    -   Detailed Task: [ComfyUI-NovaSR Integration](docs/tasks/nova_sr_integration.md)
3.  **Harmony Flags & Chord Notation:** Implementing specialized flags for transcribing chord progressions with bidirectional text parsing and spectral analysis.
    -   Detailed Task: [Harmony Flags](docs/tasks/harmony_flags.md)
4.  **AI Stem Separation:** Integrating models like Demucs to allow users to isolate Vocals, Drums, Bass, and Other instruments.
    -   Detailed Task: [Stem Separation](docs/tasks/stem_separation.md)
5.  **MIDI Capture & Export:** Enabling users to draw notes on the spectrum and export them as MIDI files.
    -   Detailed Task: [MIDI Export](docs/tasks/midi_export.md)
6.  **Advanced Loop Management:** Adding support for saving, naming, and navigating multiple loop regions.
    -   Detailed Task: [Loop Management](docs/tasks/loop_management.md)

## Working Guidelines
-   Always verify your changes by running existing tests (if any) or adding new ones.
-   Follow the technical details outlined in the specific task documents.
-   Maintain clear documentation of your progress.

## Documentation Maintenance
As an agent, you are responsible for keeping the project documentation accurate and up-to-date.

### Files to Maintain:
-   **`Readme.md`**: Update with high-level project status and setup instructions.
-   **`AGENTS.md`**: (This file) Update with major goals and guidelines.
-   **`docs/project_structure.md`**: Update whenever directories or major files are added, moved, or removed.
-   **`docs/tasks/`**: Update the status of sub-tasks (check/uncheck boxes) and add new tasks as the project evolves.

### Formatting & Style:
-   Use clear, concise Markdown.
-   Organize tasks logically and subdivide them into actionable steps.
-   Use cross-links between documentation files where appropriate.
