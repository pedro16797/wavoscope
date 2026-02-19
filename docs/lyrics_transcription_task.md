# Lyrics Transcription Tool Task Summary

This document outlines the changes made to Wavoscope to support built-in interactive lyrics transcription and MusicXML export.

## Modified and Added Files

### Frontend
- **`frontend/src/components/LyricsTimeline.tsx`** (Added): The interactive canvas track for managing lyric elements.
- **`frontend/src/components/WaveformView.tsx`**: Integrated the new track and added a "Lyrics" toggle button.
- **`frontend/src/store/types.ts`**: Updated with `Lyric` interface and refactored Slice definitions to consolidate the "Source of Truth".
- **`frontend/src/store/slices/projectSlice.ts`**: Added lyric CRUD operations, selection management, and backend synchronization.
- **`frontend/src/store/slices/playbackSlice.ts`**: Implemented `cycleLoopMode` with availability logic.
- **`frontend/src/store/slices/configSlice.ts`**: Added `showLyrics` visibility state.
- **`frontend/src/store/useStore.ts`**: Aggregated the new modular slices.
- **`frontend/src/store/useKeyboardShortcuts.ts`**: Added `Tab` (loop cycle) and `Shift+L` (deselect) shortcuts.
- **`frontend/src/components/PlaybackBar.tsx`**: Refactored looping UI to support the new `lyric` mode and store-driven cycling.
- **`frontend/src/components/Timeline.tsx`**: Enhanced the loop range highlight to update instantly when lyrics are adjusted.

### Backend & Session
- **`backend/main.py`**: Expanded the `/status` endpoint to include the `lyrics` array and calculated loop range.
- **`backend/routers/project.py`**: Created REST endpoints for adding, moving, updating, and selecting lyrics.
- **`session/project.py`**: Implemented list management for lyrics, selection tracking, and automated loop range resets upon data modification.
- **`session/looping.py`**: Added logic for the `lyric` loop mode, prioritizing selection indices.
- **`session/export.py`**: Overhauled MusicXML generation to split measures into segments at lyric/harmony timestamps, ensuring properly aligned `<lyric>` tags.

## Keyboard Shortcuts & Interactions

| Key | Action | Context |
|-----|--------|---------|
| `L` | Add/Commit Lyric | Global (Track must be visible) |
| `Shift + L` | Deselect Active Lyric | Global |
| `Tab` | Cycle Loop Modes | Global |
| `Enter` | Edit Text | Lyric Selected |
| `Arrows (L/R)` | Move Lyric | Lyric Selected |
| `Arrows (U/D)` | Resize Lyric | Lyric Selected |
| `Shift + L-Arrow`| Seek to Word Start / Prev Word | Lyric Selected |
| `Shift + R-Arrow`| Jump to Next Word | Lyric Selected |
| `Space` / `-` | Split & Advance | Inside Lyric Input |

### Mouse Interactions
- **Single Click (Empty Spot)**: Adds a new lyric element and enters edit mode.
- **Left Click (Existing Box)**: Selects the element for movement/keyboard interaction.
- **Drag (Center 80%)**: Moves the element.
- **Drag (Edge 10%)**: Resizes the element (Left/Right edges).
- **Background Click**: Deselects the current element.

## Potential Unit Tests to Include

### Backend (Python/Pytest)
- **Export Partitioning**: Verify that `generate_musicxml` correctly splits a 4-beat measure into three segments if a lyric starts at 1.5s and a harmony change occurs at 3.0s.
- **Collision Logic**: Ensure `move_lyric` and `update_lyric` maintain the 0.2s minimum duration and do not allow timestamps to exceed the file duration.
- **Persistence**: Verify that lyric data containing special characters or unicode is correctly saved to and loaded from the `.oscope` sidecar file.

### Frontend (Vitest/Testing Library)
- **Store Slices**: Test that `cycleLoopMode` correctly skips "Section" or "Bar" modes if the respective markers are missing.
- **Input Handling**: Verify that typing "Hello-" in the lyric input correctly triggers the addition of a second lyric element and removes the trailing dash from the first.
- **Selection Sync**: Ensure that `setSelectedLyricIdx` correctly triggers a POST request to the backend.

## README Documentation Updates Required
- **Workflow Guide**: Explain the "Type-Split-Advance" workflow using `L`, `Space`, and `-` for high-speed transcription.
- **Resizing Mechanics**: Document the 10% edge threshold for mouse-based resizing.
- **Looping Priority**: Clarify how the `Tab` key cycles through markers and how `lyric` loop mode depends on an active selection.
- **Visual Feedback**: Describe the auto-fading behavior for very small text boxes at high zoom levels.
