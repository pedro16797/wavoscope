"""
Core playback engine: file I/O, speed control, metronome clicks, real-time stream.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, List, Tuple, Any

import numpy as np
import sounddevice as sd
import soundfile as sf
from PySide6.QtCore import Signal, QObject
from scipy.signal import butter, sosfilt

from wavoscope.audio.ringbuffer import RingBuffer
from wavoscope.audio.synth import SimpleSynth


class AudioBackend(QObject):
    """
    Thread-safe audio backend.

    Emits
    -----
    finished : Signal()   – playback reached EOF
    """

    finished = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._data: np.ndarray | None = None          # mono float32
        self._sr: int = 44_100
        self._cursor: float = 0.0
        self._speed: float = 1.0
        self._volume: float = 1.0
        self._playing: bool = False

        self._output_buffer = RingBuffer(2 * self._sr)  # 2 s safety
        self._synth = SimpleSynth(self._sr)

        self._stream: sd.OutputStream | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        # Metronome state
        self._click_gain: float = 0.3
        self._strong_freq: float = 1_200.0
        self._weak_freq: float = 800.0
        self._metronome_enabled: bool = True

        self._subdivision_ticks_between: Callable[[float, float], List[Tuple[float, bool]]] | None = None

    # ---------- file I/O ----------
    def open_file(self, path: Path) -> None:
        """Load audio file, reset playback state."""
        data, sr = sf.read(str(path), always_2d=False, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        self._data = data.astype(np.float32)
        self._sr = sr
        self._cursor = 0.0
        self._playing = False
        self._stop_event.clear()
        self._start_stream()

    def close(self) -> None:
        """Stop stream and release resources."""
        self._stop_event.set()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    # ---------- playback control ----------
    def seek(self, sec: float) -> None:
        self._cursor = max(0.0, min(sec, self.duration))
        self.clear_tick_cache()

    def play(self) -> None:
        self._playing = True

    def pause(self) -> None:
        self._playing = False
        self.clear_tick_cache()

    def set_speed(self, speed: float) -> None:
        self._speed = max(0.1, min(speed, 4.0))

    def set_volume(self, vol: float) -> None:
        self._volume = max(0.0, min(vol, 1.0))

    def set_metronome_enabled(self, enabled: bool) -> None:
        self._metronome_enabled = enabled

    def set_click_gain(self, gain: float) -> None:
        self._click_gain = max(0.0, min(gain, 1.0))

    def set_tick_provider(self, fn: Callable[[float, float], list[tuple[float, bool]]]) -> None:
        """Inject Project.subdivision_ticks_between for metronome clicks."""
        self._subdivision_ticks_between = fn

    def clear_tick_cache(self) -> None:
        if hasattr(self, "_last_tick_time"):
            delattr(self, "_last_tick_time")

    # ---------- read-only properties ----------
    @property
    def position(self) -> float:
        return self._cursor

    @property
    def duration(self) -> float:
        return len(self._data) / self._sr if self._data is not None else 0.0

    # ---------- internal ----------
    def _start_stream(self) -> None:
        """Create (or re-create) the PortAudio output stream."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()

        self._stream = sd.OutputStream(
            samplerate=self._sr,
            channels=1,
            callback=self._audio_callback,
            finished_callback=self._on_finished,
        )
        self._stream.start()

    def _on_finished(self) -> None:
        self.finished.emit()

    # ---------- real-time callback ----------
    def _audio_callback(
        self,
        outdata: np.ndarray,
        frames: int,
        _time: Any,
        status: Any,
    ) -> None:
        """PortAudio callback executed on high-priority thread."""
        if status:
            print(f"[AudioBackend] {status}")

        # Always start with silence
        outdata[:] = 0.0

        if not self._playing or self._data is None:
            return

        # Compute how many source samples we need
        needed = int(frames * self._speed)
        start_idx = int(self._cursor * self._sr)
        end_idx = int((self._cursor + frames / self._speed) * self._sr)

        # Clamp to file boundaries
        end_idx = min(end_idx, len(self._data))
        start_idx = min(start_idx, end_idx)
        chunk = self._data[start_idx:end_idx]

        # End-of-file handling
        if chunk.size < needed:
            padding = needed - chunk.size
            chunk = np.concatenate([chunk, np.zeros(padding, dtype=np.float32)])
            self._cursor = 0.0
            self._playing = False
            self.finished.emit()
        elif chunk.size > needed:
            chunk = chunk[:needed]

        # Ensure exact length
        chunk = chunk[:frames] if chunk.size > frames else np.pad(chunk, (0, frames - chunk.size))

        # Simple anti-aliasing filter when speed < 0.9
        if self._speed < 0.9:
            low = 100 + (1.0 - self._speed) * 80
            high = 20_000 - (1.0 - self._speed) * 16_000
            sos = butter(2, [low, high], btype="band", fs=self._sr, output="sos")
            chunk = sosfilt(sos, chunk)

        # Apply volume
        outdata[:, 0] = chunk * self._volume

        # Metronome overlay
        if self._metronome_enabled and self._subdivision_ticks_between:
            self._add_metronome_clicks(outdata, frames)

        self._cursor += frames / self._sr * self._speed

    # ---------- metronome ----------
    def _add_metronome_clicks(
        self, outdata: np.ndarray, frames: int
    ) -> None:
        """Generate & inject click samples based on subdivision flags."""
        if self._subdivision_ticks_between is None:
            return

        callback_start = self._cursor
        callback_end = self._cursor + frames / self._sr

        ticks = self._subdivision_ticks_between(callback_start, callback_end)

        for tick_time, is_strong in ticks:
            if tick_time < callback_start or tick_time >= callback_end:
                continue

            offset = int((tick_time - callback_start) * self._sr)
            click_dur = min(int(0.1 * self._sr), frames - offset)
            if click_dur <= 0:
                continue

            # Determine shading from neighbouring flags
            shaded = False
            if hasattr(self._subdivision_ticks_between, "__self__"):
                flags = getattr(self._subdivision_ticks_between, "__self__").flags
                for prev, nxt in zip(flags, flags[1:]):
                    if prev.get("type") != "rhythm":
                        continue
                    subdiv = prev.get("subdivision", 1)
                    if subdiv <= 1 or not (prev["t"] <= tick_time < nxt["t"]):
                        continue

                    span = nxt["t"] - prev["t"]
                    step = span / subdiv
                    k = int((tick_time - prev["t"]) / step)
                    shaded = prev.get("shaded_subdivisions", False) and k % 2 == 1
                    break

            volume = self._click_gain * (0.5 if shaded else 1.0)
            freq = self._strong_freq if is_strong else self._weak_freq

            t = np.arange(click_dur) / self._sr
            envelope = np.exp(-t * 10)
            fundamental = np.sin(2 * np.pi * freq * t)
            harmonic = 0.3 * np.sin(2 * np.pi * freq * 2 * t)
            click = (fundamental + harmonic) * envelope * volume
            click = np.clip(click, -0.8, 0.8)

            outdata[offset : offset + click_dur, 0] += click