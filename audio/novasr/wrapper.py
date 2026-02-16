import torch
import numpy as np
import soxr
from .model import SynthesizerTrn

class NovaSR:
    def __init__(self, ckpt_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self._resampler_in = None
        self._resampler_out = None
        self._current_sr = None

        self.hps = {
            "train": {"segment_size": 9600},
            "data": {"hop_length": 320, "n_mel_channels": 128},
            "model": {
                "resblock": "0",
                "resblock_kernel_sizes": [11],
                "resblock_dilation_sizes": [[1,3,5]],
                "upsample_initial_channel": 32,
            }
        }

        if ckpt_path is None:
            try:
                from huggingface_hub import hf_hub_download
                ckpt_path = hf_hub_download(repo_id="drbaph/NovaSR", filename="NovaSR.safetensors")
            except Exception as e:
                print(f"[NovaSR] Failed to download weights: {e}")
                raise

        self.model = self._load_model(ckpt_path).eval()
        if self.device.type == 'cuda':
            self.model = self.model.half()
            self.half = True
        else:
            self.half = False

    def _load_model(self, ckpt_path):
        model = SynthesizerTrn(
            self.hps['data']['n_mel_channels'],
            self.hps['train']['segment_size'] // self.hps['data']['hop_length'],
            **self.hps['model']
        ).to(self.device)

        if ckpt_path.endswith(".safetensors"):
            from safetensors.torch import load_file
            state_dict = load_file(ckpt_path, device="cpu")
        else:
            state_dict = torch.load(ckpt_path, map_location='cpu')

        model.dec.remove_weight_norm()
        model.load_state_dict(state_dict, strict=True)
        return model

    def reset(self):
        """Reset resamplers state."""
        self._resampler_in = None
        self._resampler_out = None
        self._current_sr = None

    def enhance(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Enhance audio: Resample to 16kHz -> NovaSR -> Resample back to original SR.
        Uses stateful soxr resamplers.
        """
        if self._current_sr != sr:
            self._resampler_in = soxr.ResampleStream(sr, 16000, 1)
            self._resampler_out = soxr.ResampleStream(48000, sr, 1)
            self._current_sr = sr

        # 1. Resample to 16kHz
        audio_16k = self._resampler_in.resample_chunk(audio)

        # 2. Tensorize
        if audio_16k.size == 0:
             return np.zeros(0, dtype=np.float32)

        x = torch.from_numpy(audio_16k).float().to(self.device).view(1, 1, -1)
        if self.half:
            x = x.half()

        with torch.no_grad():
            y = self.model(x)

        audio_48k = y.view(-1).cpu().float().numpy()

        # 3. Resample back to original SR
        audio_out = self._resampler_out.resample_chunk(audio_48k)

        return audio_out
