"""
Core playback engine: file I/O, speed control, metronome clicks, real-time stream.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, List, Tuple, Any, Dict
import bisect

import numpy as np
import scipy.signal
try:
    import sounddevice as sd
except OSError:
    sd = None
import soundfile as sf

from audio.ringbuffer import RingBuffer
from audio.synth import SimpleSynth


class AudioBackend:
    """
    Thread-safe audio backend.
    """

    def __init__(self) -> None:
        self._callbacks: Dict[str, List[Callable]] = {"finished": []}

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
        self._loop_provider: Callable[[float], Tuple[float, float]] | None = None
        self._loop_enabled: bool = False
        self._active_loop_range: Tuple[float, float] | None = None

        # Pre-calculated click waveforms
        self._strong_click: np.ndarray = np.zeros(0, dtype=np.float32)
        self._weak_click: np.ndarray = np.zeros(0, dtype=np.float32)
        self._precalculate_clicks()

        # Band-pass filter state
        self._filter_enabled: bool = False
        self._filter_low_enabled: bool = True
        self._filter_high_enabled: bool = True
        self._filter_low_hz: float = 200.0
        self._filter_high_hz: float = 2000.0
        self._filter_sos: np.ndarray | None = None
        self._filter_zi: np.ndarray | None = None
        self._update_filter_coeffs()

    # ---------- file I/O ----------
    def open_file(self, path: Path) -> None:
        """Load audio file, reset playback state."""
        data, sr = sf.read(str(path), always_2d=False, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        self._data = data.astype(np.float32)
        self._sr = sr
        self._update_filter_coeffs()
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
        self._active_loop_range = None
        self.clear_tick_cache()
        if self._filter_sos is not None:
            self._filter_zi = scipy.signal.sosfilt_zi(self._filter_sos)

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
        self._precalculate_clicks()

    def set_tick_provider(self, fn: Callable[[float, float], list[tuple[float, bool]]]) -> None:
        """Inject Project.subdivision_ticks_between for metronome clicks."""
        self._subdivision_ticks_between = fn

    def set_loop_provider(self, fn: Callable[[float], Tuple[float, float]]) -> None:
        """Inject Project.get_loop_range."""
        self._loop_provider = fn

    def set_loop_enabled(self, enabled: bool) -> None:
        self._loop_enabled = enabled
        self._active_loop_range = None

    def set_filter(self,
                   enabled: bool | None = None,
                   low: float | None = None,
                   high: float | None = None,
                   low_enabled: bool | None = None,
                   high_enabled: bool | None = None) -> None:
        """Update filter settings."""
        if enabled is not None:
            self._filter_enabled = enabled
        if low_enabled is not None:
            self._filter_low_enabled = low_enabled
        if high_enabled is not None:
            self._filter_high_enabled = high_enabled

        # Enforce low < high with a small gap
        min_gap = 50.0
        new_low = low if low is not None else self._filter_low_hz
        new_high = high if high is not None else self._filter_high_hz

        # Apply constraints together
        self._filter_low_hz = max(20.0, min(new_low, new_high - min_gap))
        self._filter_high_hz = max(self._filter_low_hz + min_gap, min(new_high, self._sr / 2 - 20))

        self._update_filter_coeffs()

    def reset_loop_range(self) -> None:
        self._active_loop_range = None

    def clear_tick_cache(self) -> None:
        if hasattr(self, "_last_tick_time"):
            delattr(self, "_last_tick_time")

    def _update_filter_coeffs(self) -> None:
        """(Re)calculate SOS for the filter."""
        if not self._filter_low_enabled and not self._filter_high_enabled:
            self._filter_sos = None
            self._filter_zi = None
            return

        nyquist = max(self._sr / 2, 100.0)

        if self._filter_low_enabled and self._filter_high_enabled:
            low = max(10.0, self._filter_low_hz) / nyquist
            high = min(self._filter_high_hz, nyquist - 10.0) / nyquist
            if low >= high:
                low = high * 0.9
            self._filter_sos = scipy.signal.butter(4, [low, high], btype='bandpass', output='sos')
        elif self._filter_low_enabled:
            low = max(10.0, self._filter_low_hz) / nyquist
            self._filter_sos = scipy.signal.butter(4, low, btype='highpass', output='sos')
        else:  # high enabled
            high = min(self._filter_high_hz, nyquist - 10.0) / nyquist
            self._filter_sos = scipy.signal.butter(4, high, btype='lowpass', output='sos')

        self._filter_zi = scipy.signal.sosfilt_zi(self._filter_sos)

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
        if sd is None:
            print("[AudioBackend] sounddevice/PortAudio not available. Audio output disabled.")
            return

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
        self._emit("finished")

    def register_callback(self, event: str, callback: Callable) -> None:
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        for callback in self._callbacks.get(event, []):
            callback(*args, **kwargs)

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

        # Handle Looping
        if self._loop_enabled and self._loop_provider:
            if self._active_loop_range is None:
                self._active_loop_range = self._loop_provider(self._cursor)

            lstart, lend = self._active_loop_range
            if self._cursor >= lend - 0.001:
                self._cursor = lstart
                self.clear_tick_cache()

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
            pad = np.zeros(padding, dtype=np.float32)
            chunk = np.concatenate([chunk, pad])
            self._cursor = 0.0
            self._playing = False
            self._emit("finished")
        elif chunk.size > needed:
            chunk = chunk[:needed]
            padding = frames - needed
            if padding > 0:
                tail   = chunk[-min(len(chunk), padding):]
                mirror = tail[::-1]
                pattern = np.concatenate([mirror, tail])
                repeated = np.resize(pattern, padding)
                pad = repeated
                chunk  = np.concatenate([chunk, pad])

        # Ensure exact length
        chunk = chunk[:frames] if chunk.size > frames else np.pad(chunk, (0, frames - chunk.size))

        # Band-pass filter
        if self._filter_enabled and self._filter_sos is not None:
            chunk, self._filter_zi = scipy.signal.sosfilt(self._filter_sos, chunk, zi=self._filter_zi)

        # Apply volume
        outdata[:, 0] = chunk * self._volume

        # Metronome overlay
        if self._metronome_enabled and self._subdivision_ticks_between:
            self._add_metronome_clicks(outdata, frames)

        self._cursor += frames / self._sr * self._speed

    # ---------- metronome ----------
    def _precalculate_clicks(self) -> None:
        """Create strong/weak click waveforms to avoid generation in audio thread."""
        dur_s = 0.1
        click_dur = int(dur_s * self._sr)
        t = np.arange(click_dur) / self._sr
        envelope = np.exp(-t * 20)  # Sharper decay for better transient

        def gen_click(freq: float) -> np.ndarray:
            fundamental = np.sin(2 * np.pi * freq * t)
            harmonic = 0.3 * np.sin(2 * np.pi * freq * 2 * t)
            return ((fundamental + harmonic) * envelope).astype(np.float32)

        self._strong_click = gen_click(self._strong_freq)
        self._weak_click = gen_click(self._weak_freq)

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
            if offset < 0 or offset >= frames:
                continue

            # Determine shading efficiently
            shaded = False
            if hasattr(self._subdivision_ticks_between, "__self__"):
                project = getattr(self._subdivision_ticks_between, "__self__")
                flags = project.flags
                if flags:
                    # Find insertion point to get current/next flag
                    times = [f["t"] for f in flags]
                    idx = bisect.bisect_right(times, tick_time) - 1

                    if 0 <= idx < len(flags) - 1:
                        prev = flags[idx]
                        nxt = flags[idx + 1]
                        if prev.get("type") == "rhythm":
                            subdiv = prev.get("subdivision", 1)
                            if subdiv > 1:
                                span = nxt["t"] - prev["t"]
                                step = span / subdiv
                                k = int((tick_time - prev["t"] + 1e-6) / step)
                                shaded = prev.get("shaded_subdivisions", False) and k % 2 == 1

            volume = self._click_gain * (0.5 if shaded else 1.0)
            click_src = self._strong_click if is_strong else self._weak_click

            click_dur = min(len(click_src), frames - offset)
            if click_dur > 0:
                outdata[offset : offset + click_dur, 0] += click_src[:click_dur] * volume