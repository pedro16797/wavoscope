import onnxruntime as ort
import numpy as np
import soxr
from pathlib import Path

class NovaSR:
    def __init__(self, model_path=None):
        self._resampler_in = None
        self._resampler_out = None
        self._current_sr = None

        if model_path is None:
            # Default to bundled path relative to this file: ../../resources/models/novasr.onnx
            model_path = Path(__file__).parents[2] / "resources" / "models" / "novasr.onnx"

        if not model_path.exists():
            # Fallback for dev environment or when running from root
            alt_path = Path("resources/models/novasr.onnx")
            if alt_path.exists():
                model_path = alt_path

        if not model_path.exists():
             raise FileNotFoundError(f"NovaSR model not found at {model_path}")

        self.session = ort.InferenceSession(str(model_path))
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def reset(self):
        """Reset resamplers state."""
        self._resampler_in = None
        self._resampler_out = None
        self._current_sr = None

    def enhance(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Enhance audio: Resample to 16kHz -> NovaSR -> Resample back to original SR.
        Uses stateful soxr resamplers and ONNX Runtime for inference.
        """
        if self._current_sr != sr:
            self._resampler_in = soxr.ResampleStream(sr, 16000, 1)
            self._resampler_out = soxr.ResampleStream(48000, sr, 1)
            self._current_sr = sr

        # 1. Resample to 16kHz
        audio_16k = self._resampler_in.resample_chunk(audio)

        # 2. Inference
        if audio_16k.size == 0:
             return np.zeros(0, dtype=np.float32)

        # NovaSR expects [Batch, Channels, Time]
        x = audio_16k.reshape(1, 1, -1).astype(np.float32)

        y = self.session.run([self.output_name], {self.input_name: x})[0]

        audio_48k = y.flatten()

        # 3. Resample back to original SR
        audio_out = self._resampler_out.resample_chunk(audio_48k)

        return audio_out
