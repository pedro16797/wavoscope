# Task: MIDI Capture & Export

## Objective
Allow users to capture musical notes directly from the spectrum visualization and export them as a standard MIDI file (.mid).

## Rationale
Many transcribers use Wavoscope to identify notes and then manually enter them into a DAW (Digital Audio Workstation). Allowing them to capture notes directly in Wavoscope and export them as MIDI streamlines this workflow and reduces errors.

## Requirements

### 1. Note Capture UI
-   Allow users to click/drag on the `Spectrum` view to define note events (pitch and duration).
-   Visual representation of captured notes as rectangles (piano roll style) overlaid on the spectrum or in a dedicated pane.
-   Support for snapping to the piano keys and timeline grid.

### 2. Note Management
-   Ability to select, move, resize, and delete captured notes.
-   Group notes into "Clips" or "Tracks".

### 3. MIDI Export
-   Provide an "Export to MIDI" button.
-   Generate a Standard MIDI File (SMF) containing all captured notes, preserving their timing and pitch.

## Sub-Tasks

-   [ ] **Data Model**: Implement a `Note` and `MidiTrack` model in the backend and frontend.
-   [ ] **Frontend Implementation**:
    -   [ ] Enable mouse interactions on the `Spectrum` component for note drawing.
    -   [ ] Implement a lightweight Piano Roll overlay.
-   [ ] **MIDI Logic**:
    -   [ ] Integrate a MIDI library (e.g., `mido` for Python) to handle SMF generation.
    -   [ ] Implement the export endpoint in the FastAPI backend.
