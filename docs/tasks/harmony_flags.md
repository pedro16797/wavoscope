# Task: Harmony Flags & Chord Notation

## Objective
Implement a new type of flag called "Harmony Flags" that allows musicians to transcribe chord progressions independently of existing rhythm/marker flags.

## Rationale
Transcribing a song often involves two parallel processes: identifying the rhythm and structure (markers), and identifying the harmony (chords). Currently, Wavoscope only supports general-purpose flags. Adding dedicated Harmony Flags with specialized UI for chord notation will significantly speed up the harmonic transcription process.

## Requirements

### 1. Interaction & Visuals
-   **Add Flag**: Right-click on the timeline or waveform should create a Harmony Flag.
-   **Draggable**: Harmony Flags should be draggable along the timeline, just like normal flags.
-   **Visually Distinct**: Harmony Flags should have a different color or shape from normal flags to avoid confusion.
-   **Independence**: They should exist in a separate collection from existing flags to allow for overlapping without interference.

### 2. Chord Entry Menu
Upon creating a Harmony Flag, a specialized menu/dialog should appear to describe the chord:
-   **Root Note**: Selectors for A to G and a dropdown for accidentals (# or b).
-   **Chord Quality**: Dropdown for quality (M, m, dim, aug, sus2, sus4, etc.).
-   **Extension**: Select whether it's a triad, seventh chord, or extended (9, 11, 13).
-   **Altered Notes**: An array/list of altered notes (e.g., #5, b9).
-   **Added Tones**: An array/list of added tones (e.g., add9, add13).
-   **Bass Note**: Optional field for the bass note (slash chords like C/E).

### 3. Bidirectional Chord Parsing
-   **Text Field**: At the top of the chord menu, a text field should display the chord name in standard notation (e.g., "Cm7b5/Eb").
-   **Live Update**: The text field should update automatically as the user changes the selectors.
-   **Parsing**: Users should be able to type directly into this text field. The application must parse the string and update all selectors accordingly.

### 4. Spectral Analysis & Auto-Fill
-   **Initial Suggestion**: When a Harmony Flag is added, the system should analyze the audio spectrum at that exact time position.
-   **Note Detection**: Identify the most prominent frequencies/notes playing at that moment.
-   **Pre-fill**: Attempt to guess the chord and pre-fill the menu fields to provide the musician with a starting point.

## Sub-Tasks

-   [ ] **Backend State**: Update `Project` class and `Flag` model to support a new `type` or separate collection for Harmony Flags.
-   [ ] **API Endpoints**: Create endpoints for creating, updating, and deleting Harmony Flags.
-   [ ] **Frontend Implementation**:
    -   [ ] Handle right-click event on `Timeline` and `Waveform` components.
    -   [ ] Implement the Harmony Flag visual component.
    -   [ ] Create the `ChordDialog` component with all required selectors.
-   [ ] **Chord Logic**:
    -   [ ] Implement the bidirectional parsing logic for chord notation.
    -   [ ] Integrate the spectral analysis logic to provide chord suggestions.
