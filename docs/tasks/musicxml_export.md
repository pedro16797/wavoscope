# Task: MusicXML Export

## Objective
Export the project's transcription data (rhythm, sections, and harmony) as a standard MusicXML file for use in notation software (like MuseScore, Sibelius, or Finale).

## Rationale
MusicXML is the industry standard for exchanging sheet music data. By exporting to MusicXML, transcribers can take their work in Wavoscope and immediately have a structured score template with sections, time signatures, and chords already in place.

## Requirements

### 1. Data Sources
The export should synthesize information from:
-   **Rhythm Flags**: To determine measure boundaries, rhythm subdivisions, and dynamic tempo changes.
-   **Section Markers**: To create section headings or rehearsal marks in the score.
-   **Harmony Flags**: To include chord symbols above the staff.
-   **Project Metadata**: For default time signature and other score-level information.

### 2. Export Content
The generated MusicXML should include:
-   **Sections**: Proper rehearsal marks or text annotations for sections.
-   **Time Signature**: Support for various time signatures (e.g., 4/4, 7/8, 3/4).
-   **Dynamic Tempo**:
    -   Calculate tempo (BPM) dynamically based on the time interval between rhythm flags.
    -   A tempo change should be recorded in the MusicXML file only when the calculated BPM differs by more than **5 BPM** from the last recorded tempo marker.
-   **Chords**: Accurate MusicXML `<harmony>` tags based on the Harmony Flags.
-   **Rhythm**: Basic measure structure based on the rhythm flags.

### 3. UI
-   An "Export as MusicXML" option in the project menu.

## Sub-Tasks

-   [ ] **Schema Update**: Ensure `Project` data captures default time signature information if not already present.
-   [ ] **MusicXML Generation Logic**:
    -   [ ] Implement a generator that iterates through project flags and builds the MusicXML tree.
    -   [ ] Implement dynamic tempo calculation logic with the 5 BPM threshold.
    -   [ ] Map internal chord representations (from Harmony Flags) to MusicXML chord structures.
-   [ ] **API & UI**:
    -   [ ] Create a backend endpoint to generate and serve the `.xml` / `.musicxml` file.
    -   [ ] Add the export button to the frontend.
