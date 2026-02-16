# Task: AI Stem Separation (Demucs Integration)

## Objective
Integrate an AI-based stem separation model to allow users to isolate different components of the audio (e.g., Vocals, Drums, Bass, Other) directly within Wavoscope.

## Rationale
Musicians transcribing complex arrangements often struggle to hear individual instruments in a full mix. Stem separation allows them to isolate the instrument they are focusing on, drastically improving accuracy and reducing the time spent on transcription.

## Requirements

### 1. Model Integration
-   Integrate a high-quality, open-source stem separation model (e.g., **Facebook/Meta's Demucs** or **Spleeter**).
-   Demucs is preferred for its higher quality, though it is more computationally intensive.

### 2. Processing Pipeline
-   Implement an asynchronous processing task to handle the separation, as it may take several minutes for a full song.
-   Store the separated stems as temporary or project-linked audio files.

### 3. Frontend Controls
-   Add a "Stems" or "Isolate" panel in the UI.
-   Provide sliders or toggles for each stem (Vocals, Drums, Bass, Other) to adjust their volume or solo/mute them during playback.
-   Visual feedback for processing progress (progress bar).

## Sub-Tasks

-   [ ] **Model Research**: Evaluate the performance and size of different Demucs variants (e.g., `mdx_extra_q`).
-   [ ] **Backend Implementation**:
    -   [ ] Add necessary dependencies (`demucs`, `torch`).
    -   [ ] Create a stem separation service/worker.
    -   [ ] Implement API endpoints to trigger separation and fetch status.
-   [ ] **Audio Engine Update**:
    -   [ ] Modify `AudioBackend` to support multi-track playback or dynamic mixing of stems.
-   [ ] **Frontend Implementation**:
    -   [ ] Create a Stem Control UI component.
    -   [ ] Integrate stem volume controls with the playback engine.
