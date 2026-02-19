# Lyrics Transcription & Alignment

Wavoscope provides a dedicated lyrics track for interactive transcription, word-level alignment, and MusicXML export. This feature is designed for rapid entry and precise timing adjustment.

## Core Concepts

### The Lyrics Track
The lyrics track is a specialized canvas-based track located above the main waveform. It displays lyric elements as editable boxes.
- **Visibility:** Toggle the track using the "Lyrics" button in the waveform header.
- **Scaling:** The track height is fixed (32px), but its content scales with the global zoom and offset.
- **Selection:** Only one lyric can be selected at a time. Selecting a lyric highlights it and enables specific keyboard shortcuts.

### Transcription Workflow: "Type-Split-Advance"
The most efficient way to transcribe a song is using the following workflow:
1.  **Start:** Press `L` or click an empty spot to create the first lyric at the current playhead.
2.  **Type:** Enter the first word.
3.  **Split:** Press `Space` (for new words) or `-` (for syllables within a word). This commits the current text and immediately spawns a new lyric box.
    - **Visual Differentiation:** Words split by hyphens (syllables) are visually connected by a horizontal line in the timeline. The hyphen itself is stored in the data but hidden in the UI when not editing, providing a clean look.
4.  **Repeat:** Focus is automatically transferred to the new box, allowing you to continue transcribing as the music plays.
5.  **Commit:** Press `Enter` or click elsewhere to finish editing.

## Interaction & Shortcuts

### Mouse Control
- **Single Click (Empty Space):** Adds a new lyric at that timestamp and enters edit mode.
- **Left Click (Existing Box):** Selects the lyric.
- Single Click (Selected Box): Deselects the lyric.
- **Drag (Center 80%):** Moves the lyric element along the timeline.
- **Drag (Edges 10%):** Resizes the lyric. Dragging the left edge adjusts the start time; dragging the right edge adjusts the duration.
- **Double Click:** Enters edit mode for the clicked lyric.
- **Background Click:** Deselects the current lyric.

### Keyboard Shortcuts

| Key | Action | Context |
|-----|--------|---------|
| `L` | Add / Commit & Advance | Global |
| `Shift + L` | Deselect All | Global |
| `Tab` | Cycle Loop Modes | Global |
| `Enter` | Start/Finish Editing | Selected |
| `Escape` | Cancel Editing / Deselect | Selected |
| `Arrows (Left/Right)` | Nudge Position (0.1s) | Selected (Not editing) |
| `Arrows (Up/Down)` | Adjust Duration (0.1s) | Selected (Not editing) |
| `Shift + Arrows` | Seek between Lyrics | Global / Selected |
| `Space` / `-` | Commit & Spawn Next | Editing |

## Technical Implementation

### Frontend
- **`LyricsTimeline.tsx`**: Uses a Ref-based state management system to handle high-frequency interactions (dragging) locally before committing to the backend. It employs a `ResizeObserver` for responsive canvas rendering.
- **State Management**: Integrated into `projectSlice.ts`. CRUD operations are optimized to update local state directly from backend responses, minimizing network round-trips.
- **Visuals**: Features a dynamic rendering engine that handles text truncation and fading for small elements.

### Backend
- **Data Structure**: Lyrics are stored as a sorted list of objects `{text, timestamp, duration}` in the `.oscope` sidecar file.
- **Looping Engine**: The `LoopingEngine` supports a `lyric` mode, which automatically sets the loop range to the currently selected lyric.
- **MusicXML Export**: `session/export.py` splits measures into segments at every lyric and harmony boundary. This ensures that `<lyric>` tags are perfectly aligned with the rhythmic structure in the exported score.

## Alignment Tips
- **High Zoom:** For word-level alignment, zoom in until you can clearly see the transients in the waveform.
- **Looping:** Use the `lyric` loop mode (cycle with `Tab`) to repeat the current word while you fine-tune its start and end points.
- **Metronome:** Keep subdivision clicks on to ensure your lyrics align with the underlying beat markers (Rhythm Flags).
