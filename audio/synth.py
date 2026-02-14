"""
Simple real-time sine-wave synthesiser for live piano-style playback.
"""
from __future__ import annotations

from typing import Any, Dict

import numpy as np
try:
    import sounddevice as sd
except OSError:
    sd = None


class SimpleSynth:
    """
    Generates one or more sine waves with shared phase state.

    Designed for instantaneous key presses; no envelope beyond a fixed 0.2 gain.
    """

    def __init__(self, sr: int = 44_100) -> None:
        self.sr: int = sr
        self._active: Dict[float, float] = {}  # freq -> current phase (seconds)

        if sd is not None:
            try:
                self._stream = sd.OutputStream(
                    samplerate=self.sr,
                    channels=1,
                    callback=self._callback,
                )
                self._stream.start()
            except Exception as e:
                print(f"[SimpleSynth] Failed to start stream: {e}")
                self._stream = None
        else:
            self._stream = None

    # ---------- public ----------
    def start_tone(self, freq: float) -> None:
        """Begin a sine at `freq` Hz (idempotent)."""
        self._active[freq] = 0.0

    def stop_tone(self, freq: float) -> None:
        """Stop a sine at `freq` Hz if running."""
        self._active.pop(freq, None)

    def stop_all(self) -> None:
        """Silence every active tone."""
        self._active.clear()

    # ---------- audio callback ----------
    def _callback(
        self,
        outdata: np.ndarray,
        frames: int,
        _time: Any,
        _status: Any,
    ) -> None:
        """PortAudio callback: fill `outdata` with the summed sine bank."""
        t = np.arange(frames) / self.sr
        out = np.zeros(frames, dtype=np.float32)

        for freq, phase in list(self._active.items()):
            wave = 0.2 * np.sin(2 * np.pi * freq * (t + phase))
            out += wave.astype(np.float32)
            self._active[freq] = phase + frames / self.sr

        # Normalise when many tones overlap
        out *= 0.8 / max(1, len(self._active))
        outdata[:] = out.reshape(-1, 1)