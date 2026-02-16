# Task: Monolithic Script Refactoring

## Objective
Split large, monolithic scripts into smaller, more focused modules to improve maintainability, testability, and readability.

## Candidates for Splitting

### 1. `audio/audio_backend.py`
This script currently handles several distinct responsibilities.
- **Proposed Split**:
    - `audio/engine/playback.py`: Core playback state and PortAudio stream management.
    - `audio/engine/processing.py`: TSM (Signalsmith) and NovaSR enhancement logic.
    - `audio/engine/metronome.py`: Click generation and subdivision logic.
    - `audio/engine/filters.py`: DSP filter (SOS) management.

### 2. `main.py` (Root)
Combines backend orchestration, GUI setup (pywebview), and a health check loop.
- **Proposed Split**:
    - `cli/launcher.py`: Logic for starting the FastAPI server and checking health.
    - `cli/gui.py`: `pywebview` configuration and JS API implementation.
    - Keep `main.py` as a minimal entry point that calls these modules.

### 3. `frontend/src/store/useStore.ts`
The central store has grown very large, containing interfaces, utility functions, and all state actions.
- **Proposed Split**:
    - `frontend/src/store/types.ts`: Shared interfaces (Flag, Chord, HarmonyFlag, AppState).
    - `frontend/src/store/utils.ts`: Helper functions like `midiToFreq`, `formatChord`, and `getChordMidiNotes`.
    - `frontend/src/store/slices/`: Modular store slices (e.g., `playbackSlice.ts`, `projectSlice.ts`, `configSlice.ts`).

### 4. `session/project.py`
Manages project persistence, flag logic, and coordinates between backend and data.
- **Proposed Split**:
    - `session/manager.py`: File I/O and sidecar persistence.
    - `session/flags.py`: Logic for rhythm and harmony flag management (sorting, auto-naming).
    - `session/looping.py`: Logic for determining loop ranges.

## Implementation Plan
- [ ] Identify and isolate logical boundaries within each monolithic script.
- [ ] Extract shared types and utilities into common modules.
- [ ] Refactor scripts one by one, ensuring all tests pass after each split.
- [ ] Update imports across the entire project to reflect the new structure.
