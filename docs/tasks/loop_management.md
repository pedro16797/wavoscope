# Task: Marker-Based Loop Management

## Objective
Enhance the looping system to use existing flags and section markers for quick, intelligent looping.

## Rationale
Rather than manually setting loop points, musicians often want to loop a specific section they have already marked, or a single bar between two rhythm flags. Automating this using existing markers speeds up the workflow.

## Requirements

### 1. Looping Modes
Implement a toggle that cycles through three looping modes:
-   **Loop Whole Song**: Standard behavior where the whole file plays repeatedly (if looping is on).
-   **Loop Current Section**: Loops between the most recent flag marked as `is_section_start` and the next section start (or the end of the song).
-   **Loop Current Bar**: Loops between the flag immediately preceding the playhead and the flag immediately following it.

### 2. UI Controls
-   A single button in the `PlaybackBar` that toggles between these modes (Icon should change to reflect the mode).
-   Visual indication on the `Timeline` of the currently active loop range for the selected mode.

### 3. Logic
-   The loop boundaries should update dynamically as the playhead moves across markers (for "Current Bar" and "Current Section" modes).
-   If no markers exist, it should fallback to looping the whole song.

## Sub-Tasks

-   [ ] **Backend Logic**:
    -   [ ] Update `Project.py` to provide helper methods for finding section and bar boundaries relative to the current position.
-   [ ] **Frontend Implementation**:
    -   [ ] Add a "Loop Mode" selector to the `PlaybackBar`.
    -   [ ] Update the `Timeline` to highlight the dynamic loop range.
    -   [ ] Update the loop toggle logic in the store to respect the chosen mode.
