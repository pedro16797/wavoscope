# Agent Guidance for Wavoscope

Welcome, Agent. This document serves as the primary entry point for understanding the current goals and tasks in the Wavoscope repository.

## Project Overview
Wavoscope is a musician-oriented audio transcription workbench. It is a desktop application built with a React frontend and a FastAPI backend.

## Main Objectives
We are currently focusing on:

1.  **Lyrics Support:** Implement a system to display and edit lyrics alongside the audio.
    -   Support for importing lyrics from text files.
    -   Visual representation of lyrics on the timeline.
2.  **AI Transcription & Alignment:** Leverage AI models to automate the transcription process.
    -   Investigate AI models (e.g., Whisper) for initial song transcription.
    -   Implement an alignment feature where users provide lyrics and the model automatically assigns timestamps to words or lines.

## Working Guidelines
-   Always verify your changes by running existing tests (if any) or adding new ones.
-   Follow the technical details outlined in specific task documents in `docs/tasks/`.
-   Maintain clear documentation of your progress.

## Documentation Maintenance
As an agent, you are responsible for keeping the project documentation accurate and up-to-date.

### Files to Maintain:
-   **`Readme.md`**: Update with high-level project status and setup instructions.
-   **`AGENTS.md`**: (This file) Update with major goals and guidelines.
-   **`docs/project_structure.md`**: Update whenever directories or major files are added, moved, or removed.
-   **`docs/tasks/`**: Create and update task documents as the project evolves.

### Formatting & Style:
-   Use clear, concise Markdown.
-   Organize tasks logically and subdivide them into actionable steps.
-   Use cross-links between documentation files where appropriate.
