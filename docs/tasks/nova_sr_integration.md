# Task: Audio Quality Enhancement & NovaSR Integration

## Objective
Implement high-quality time-scale modification (TSM) for playback speed control and integrate NovaSR for real-time audio super-resolution enhancement in Wavoscope.

## Rationale
The current playback engine uses a crude mirroring/padding technique to handle speed changes, which results in significant audio artifacts and loss of clarity. To provide a professional transcription experience, we need a proper TSM algorithm to change speed without affecting pitch, supplemented by AI super-resolution to recover high-frequency detail at slow speeds.

## State-of-the-Art (SotA) Study

### 1. Current Solution (Mirroring/Padding)
-   **Implementation**: `audio/audio_backend.py` (lines 186-191).
-   **Pros**: Zero computational overhead.
-   **Cons**: Terrible audio quality; causes metallic buzzing and "comb filter" artifacts due to sample repetition/mirroring. Does not preserve transients or harmonic structure.

### 2. Time-Scale Modification (TSM) Alternatives
| Library | Quality | Performance | Size | License | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rubber Band** | Excellent | Fast (R2/R3) | Med | GPL | Industry standard for music; R3 engine is very high quality. |
| **Signalsmith Stretch**| Very Good | Very Fast | Tiny | MIT | Single-header C++, handles multiple octaves, ideal for modern apps. |
| **SoundTouch** | Good | Excellent | Small | LGPL | Very low latency (<100ms), optimized for real-time. |
| **Librosa (PV)** | Average | Slow | N/A | ISC | Phase Vocoder based; prone to phasiness and transient smearing. |

**Recommendation for TSM**: **Signalsmith Stretch** is the preferred choice for its permissive MIT license, extreme efficiency, and high quality specifically for polyphonic music.

### 3. Audio Super-Resolution (SR) Alternatives
| Model | Quality | Performance | Size | License | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NovaSR** | High | **3600x RT** | **52 KB** | Apache-2.0 | Extremely efficient; designed for 16kHz -> 48kHz upscaling. |
| **FlowHigh** | High | 20x RT | 450 MB | ? | Good balance but much larger/slower than NovaSR. |
| **FlashSR** | High | 14x RT | 1 GB | ? | Fast diffusion-based model. |
| **AudioSR** | Very High | 0.6x RT | 5.9 GB | MIT | Highest quality but too slow for real-time desktop playback. |

**Recommendation for SR**: **NovaSR** is the clear winner for real-time integration due to its tiny footprint and incredible inference speed.

## Sub-Tasks

### 1. MVP: High-Quality TSM
-   [x] Integrate `python-stretch` (Signalsmith Stretch) into the `AudioBackend`.
-   [x] Replace the crude mirroring/padding in `_audio_callback` with the TSM engine.
-   [x] Implement smooth speed transitions and verify stability across the 0.1x - 4.0x range.

### 2. MVP: NovaSR Enhancement
-   [x] Integrate the NovaSR model and its required dependencies (`onnxruntime`, `soxr`).
-   [x] Implement the super-resolution stage in the audio pipeline: `Source -> TSM -> NovaSR -> Output`.
-   [x] Add a "High Quality Enhancement" toggle in the frontend Settings.

### 3. Performance & Quality Validation
-   [x] Test the integrated pipeline on real-world music transcription scenarios.
-   [x] Verify that CPU/RAM usage remains acceptable for real-time desktop use.
-   [x] Implement 1.0x bypass and artifact-free chunking (cross-fading).
-   [x] Document any remaining limitations or future optimization paths.

## Implementation Notes
- **TSM**: Uses `Signalsmith Stretch` via `python-stretch`. Implemented with a `RingBuffer` to handle variable output length.
- **NovaSR**: Implemented using `onnxruntime` with a bundled ONNX model (`resources/models/novasr.onnx`). Uses `soxr.ResampleStream` for stateful resampling between original SR, 16kHz (model input), and 48kHz (model output). This approach avoids heavy PyTorch dependencies and ensures compatibility with standalone builds.
- **1.0x Bypass**: To ensure zero-latency and bit-perfect playback at normal speed, the `_audio_callback` implements a direct-read bypass when `speed == 1.0`.
- **Artifact Resolution**: To eliminate "pulsating clicks" at chunk boundaries, the backend uses a 512-sample overlap-add/cross-fade mechanism between processed audio blocks.
- **Configuration Propagation**: Managed via `high_quality_enhancement` setting. A bug in the FastAPI routers was identified where the setting was not being correctly passed to the `AudioBackend`; this was resolved by updating the `AppConfig` model and `update_config` router.
