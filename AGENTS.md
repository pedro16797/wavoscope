# Agent Guidance for Wavoscope

Welcome, Agent. This document serves as the primary entry point for understanding the current goals and tasks in the Wavoscope repository.

## Project Overview
Wavoscope is a musician-oriented audio transcription workbench. Currently, it is a desktop application built with Python and PySide6 (Qt).

## Main Objectives
We are currently focusing on three major initiatives:

1.  **GUI Migration (Qt to React):** Replacing the current Qt-based interface with a browser-based GUI using React and a Python backend (e.g., FastAPI). This aims to reduce project size and improve portability.
    -   Detailed Task: [Replace Qt with React](docs/tasks/qt_to_react.md)
2.  **Quality & Performance Audit:** A comprehensive review of the project to identify bugs, optimize performance, and ensure code quality.
    -   Detailed Task: [Bugs and Performance improvements](docs/tasks/bugs_and_performance.md)
3.  **Audio Quality Enhancement (NovaSR):** Studying and integrating the ComfyUI-NovaSR model for audio super-resolution to improve the quality of slowed-down playback.
    -   Detailed Task: [ComfyUI-NovaSR Integration](docs/tasks/nova_sr_integration.md)

## Working Guidelines
-   Always verify your changes by running existing tests (if any) or adding new ones.
-   Follow the technical details outlined in the specific task documents.
-   Maintain clear documentation of your progress.
