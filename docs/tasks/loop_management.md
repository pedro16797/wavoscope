# Task: Advanced Loop Management

## Objective
Enhance the looping functionality by allowing users to save, name, and quickly navigate between multiple loop regions.

## Rationale
Transcribers often work on one section (e.g., Verse, Chorus, Solo) at a time. Being able to save these sections as named loops makes it much easier to jump back and forth between different parts of the song without manually re-adjusting the loop markers every time.

## Requirements

### 1. Saved Loops List
-   A new panel or dropdown that lists all saved loops for the current project.
-   Each entry should show the loop name and its time range.

### 2. Loop Interaction
-   Ability to "Save Current Loop": Creates a new entry from the active loop markers.
-   Ability to "Rename Loop": Give meaningful names like "Bridge" or "Hard Riff".
-   One-click Activation: Clicking a loop in the list immediately sets the active loop markers and jumps the playhead to the start of that loop.

### 3. Keyboard Shortcuts
-   Shortcuts to cycle through saved loops (e.g., `[` and `]`).
-   Shortcut to toggle the current loop on/off.

## Sub-Tasks

-   [ ] **Backend Persistence**: Update the `Project` schema to store an array of `SavedLoop` objects.
-   [ ] **Frontend Implementation**:
    -   [ ] Create a `LoopManager` component.
    -   [ ] Add visual indicators for saved loops on the `Timeline`.
    -   [ ] Integrate with the existing playback engine's looping logic.
