# Task: Spectral Band Pass Filter

## Objective
Implement a real-time band pass filter that allows musicians to isolate or focus on specific frequency ranges during playback.

## Rationale
While transcribing, it is often helpful to filter out low-end rumble or high-end hiss to hear the target instrument more clearly (e.g., boosting the mids to hear a guitar solo or cutting the highs to focus on the bass). Integrating this directly into the spectrum view makes it intuitive for the user to select the frequencies they want to hear.

## Requirements

### 1. Filter Engine
-   Implement a high-quality, low-latency band pass filter in the `AudioBackend`.
-   The filter should be adjustable in real-time without causing audio artifacts (pops/clicks).
-   Support for bypassing the filter (on/off toggle).

### 2. Spectrum UI Integration
-   Add draggable "handles" or an overlay area directly on the `Spectrum` component to define the low and high cutoff frequencies.
-   Visual feedback should clearly show which part of the spectrum is being passed and which is being attenuated (e.g., shading the filtered-out areas).

### 3. Controls
-   A toggle to enable/disable the filter.
-   Perhaps a "Solo" mode where the user can quickly sweep through frequencies.

## Sub-Tasks

-   [ ] **Backend Implementation**:
    -   [ ] Integrate a digital filter (e.g., using `scipy.signal` for design and manual implementation in the audio callback).
    -   [ ] Add API endpoints for setting filter parameters (low-cut, high-cut, enabled).
-   [ ] **Frontend Implementation**:
    -   [ ] Add interactive filter range selectors to the `Spectrum.tsx` component.
    -   [ ] Add a filter toggle button to the `PlaybackBar` or a dedicated "Audio Tools" panel.
