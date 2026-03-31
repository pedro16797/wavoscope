"""
Simple real-time sine-wave synthesiser for live piano-style playback.
"""
from __future__ import annotations

import threading
from typing import Any, Dict

import numpy as np
from utils.logging import logger
try:
    import sounddevice as sd
except OSError:
    sd = None


class SimpleSynth:
    """
    Generates one or more sine waves with shared phase state.

    Designed for instantaneous key presses; no envelope beyond a fixed 0.2 gain.
    """

    def __init__(self, sr: int = 44_100, device: int | str | None = None) -> None:
        self.sr: int = sr
        self._active: Dict[float, float] = {}  # freq -> current phase (seconds)
        self._lock = threading.RLock()
        self._device: int | str | None = device
        self._stream: sd.OutputStream | None = None

        if sd is not None:
            self._start_stream()
        else:
            logger.warning("sounddevice/PortAudio not available. Synth output disabled.")

    def _start_stream(self) -> None:
        if sd is None: return
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
        try:
            self._stream = sd.OutputStream(
                samplerate=self.sr,
                channels=1,
                callback=self._callback,
                device=self._device,
            )
            self._stream.start()
        except Exception as e:
            logger.error(f"Failed to start synth stream on device {self._device}: {e}")
            self._stream = None

    def set_device(self, device: int | str | None) -> None:
        """Update the output device and restart the stream."""
        if self._device == device: return
        self._device = device
        self._start_stream()

    # ---------- public ----------
    def start_tone(self, freq: float) -> None:
        """Begin a sine at `freq` Hz (idempotent)."""
        with self._lock:
            self._active[freq] = 0.0

    def stop_tone(self, freq: float) -> None:
        """Stop a sine at `freq` Hz if running."""
        with self._lock:
            self._active.pop(freq, None)

    def stop_all(self) -> None:
        """Silence every active tone."""
        with self._lock:
            self._active.clear()

    def close(self) -> None:
        """Stop and close the audio stream."""
        if hasattr(self, "_stream") and self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    # ---------- audio callback ----------
    def _callback(
        self,
        outdata: np.ndarray,
        frames: int,
        _time: Any,
        _status: Any,
    ) -> None:
        """PortAudio callback: fill `outdata` with the summed sine bank."""
        outdata[:] = 0
        if not self._lock.acquire(blocking=False):
            return

        try:
            if not self._active:
                return

            t = (np.arange(frames, dtype=np.float32) / self.sr)
            out = np.zeros(frames, dtype=np.float32)

            # Take a snapshot of items while locked
            active_items = list(self._active.items())

            for freq, phase in active_items:
                # Use float32 for the entire calculation
                wave = 0.2 * np.sin(2 * np.pi * freq * (t + phase)).astype(np.float32)
                out += wave

                # Apply modulo to phase to prevent precision loss over time
                # Only update if the note is still active (it might have been stopped during processing)
                if freq in self._active:
                    period = 1.0 / freq
                    self._active[freq] = (phase + frames / self.sr) % period

            # Normalise when many tones overlap
            out *= 0.8 / max(1, len(self._active))
            outdata[:] = out.reshape(-1, 1)
        finally:
            self._lock.release()