# Agent Guidance for Wavoscope

Welcome, Agent. This document serves as the primary entry point for understanding the current goals, technical standards, and safety protocols for Wavoscope.

## Project Overview
Wavoscope is a musician-oriented audio transcription workbench. It is a desktop application built with a React frontend and a FastAPI backend.

## Main Objectives
We are currently focusing on:

1.  **AI Transcription & Alignment:** Leverage AI models to automate the transcription process.
    -   Investigate AI models (e.g., Whisper) for initial song transcription.
    -   Implement an alignment feature where users provide lyrics and the model automatically assigns timestamps to words or lines.
2.  **Performance Optimization:** Ensure the CQT and Waveform rendering remains smooth on lower-end hardware.
3.  **UI Refinement:** Improve the accessibility and discoverability of advanced features like the band-pass filter and chord suggestions.

*Note: Basic Lyrics support has been integrated; focus is now on automation and refinement.*

## Core Directives (Agent Guardrails)
To maintain the stability of this precision audio tool, you must follow these directives:

-   **Minimize Blast Radius:** Touch **only** the files and functions required for your specific task. Avoid "drive-by improvements" or unrelated refactoring.
-   **Solve One Problem at a Time:** Keep your PRs/commits focused. Do not mix feature additions with architectural changes unless strictly necessary.
-   **Verify Everything:** Use `list_files`, `read_file`, and `run_in_bash_session` to confirm every modification.
-   **Test-Driven Execution:** If a test exists for a modified path, run it immediately. If not, consider if a simple unit test can be added.
-   **Preserve Interfaces:** Do not change existing API endpoints or data structures unless the task explicitly requires it.

## Working Workflow

1.  **Plan:** Propose a detailed plan before making changes.
2.  **Isolate:** Work on the minimum subset of code needed.
3.  **Validate:** Run `pytest` for backend changes and use Playwright for UI changes.
4.  **Review:** Perform a self-review or request a review on your diff before finalizing.

## Documentation Maintenance
As an agent, you are responsible for keeping the project documentation accurate and up-to-date.

### Files to Maintain:
-   **`Readme.md`**: Update with high-level project status and setup instructions.
-   **`AGENTS.md`**: (This file) Update with major goals and guidelines.
-   **`docs/project_structure.md`**: Update whenever directories or major files are added, moved, or removed.

### Formatting & Style:
-   Use clear, concise Markdown.
-   Use cross-links between documentation files where appropriate.
