"""
Core playback engine: file I/O, speed control, metronome clicks, real-time stream.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, List, Tuple, Any, Dict
import traceback

import numpy as np
import soundfile as sf

from audio.synth import SimpleSynth
from audio.engine.playback import PlaybackEngine
from audio.engine.processing import AudioProcessor
from audio.engine.metronome import MetronomeEngine
from audio.engine.filters import FilterEngine


class AudioBackend:
    """
    Thread-safe audio backend facade.
    """

    def __init__(self) -> None:
        self._playback = PlaybackEngine()
        self._processor = AudioProcessor(self._playback._sr)
        self._metronome = MetronomeEngine(self._playback._sr)
        self._filters = FilterEngine(self._playback._sr)

        self._synth = SimpleSynth(self._playback._sr)

        self._read_sample_idx: int = 0
        self._stop_event = threading.Event()

        # Looping state
        self._loop_enabled: bool = False
        self._loop_provider: Callable[[float], Tuple[float, float]] | None = None
        self._active_loop_range: Tuple[float, float] | None = None

        self._subdivision_ticks_between: Callable[[float, float], List[Tuple[float, bool]]] | None = None

    # ---------- file I/O ----------
    def open_file(self, path: Path) -> None:
        """Load audio file, reset playback state."""
        with self._playback._lock:
            data, sr = sf.read(str(path), always_2d=False, dtype="float32")
            if data.ndim > 1:
                data = data.mean(axis=1)
            data = data.astype(np.float32)

            self._playback.set_data(data, sr)
            self._processor.reset(sr)
            self._metronome.set_sr(sr)
            self._filters.set_sr(sr)

            self._read_sample_idx = 0
            self._stop_event.clear()

            self._playback.start_stream(self._audio_callback)

    def close(self) -> None:
        """Stop stream and release resources."""
        self._stop_event.set()
        self._playback.stop_stream()

    # ---------- playback control ----------
    def seek(self, sec: float) -> None:
        with self._playback._lock:
            self._playback.seek(sec)
            self._active_loop_range = None
            self._filters.reset_zi()

            self._read_sample_idx = int(self._playback.position * self._playback._sr)
            self._processor.reset()
            self.clear_tick_cache()

    def play(self) -> None:
        self._playback.play()

    def pause(self) -> None:
        self._playback.pause()
        self.clear_tick_cache()

    def set_speed(self, speed: float) -> None:
        with self._playback._lock:
            self._playback.set_speed(speed)
            self._processor.set_speed(self._playback._speed)
            self._read_sample_idx = int(self._playback.position * self._playback._sr)

    def set_volume(self, vol: float) -> None:
        self._playback.set_volume(vol)

    def set_metronome_enabled(self, enabled: bool) -> None:
        self._metronome.set_enabled(enabled)

    def set_novasr_enabled(self, enabled: bool) -> None:
        self._processor.set_novasr_enabled(enabled)

    def set_click_volume(self, volume: float) -> None:
        self._metronome.set_volume(volume)

    def set_tick_provider(self, fn: Callable[[float, float], list[tuple[float, bool]]]) -> None:
        self._subdivision_ticks_between = fn

    def set_loop_provider(self, fn: Callable[[float], Tuple[float, float]]) -> None:
        self._loop_provider = fn

    def set_loop_enabled(self, enabled: bool) -> None:
        self._loop_enabled = enabled
        if not enabled:
            self._active_loop_range = None

    def set_filter(self, **kwargs) -> None:
        with self._playback._lock:
            self._filters.set_filter(**kwargs)

    def reset_loop_range(self) -> None:
        self._active_loop_range = None

    def clear_tick_cache(self) -> None:
        if hasattr(self, "_last_tick_time"):
            delattr(self, "_last_tick_time")

    # ---------- read-only properties ----------
    @property
    def position(self) -> float:
        return self._playback.position

    @property
    def duration(self) -> float:
        return self._playback.duration

    @property
    def _playing(self) -> bool:
        return self._playback._playing

    @property
    def _data(self) -> np.ndarray | None:
        return self._playback._data

    @property
    def _sr(self) -> int:
        return self._playback._sr

    @property
    def _speed(self) -> float:
        return self._playback._speed

    @property
    def _volume(self) -> float:
        return self._playback._volume

    @property
    def _metronome_enabled(self) -> bool:
        return self._metronome._metronome_enabled

    @property
    def _click_volume(self) -> float:
        return self._metronome._click_volume

    @property
    def _filter_enabled(self) -> bool:
        return self._filters._enabled

    @property
    def _filter_low_enabled(self) -> bool:
        return self._filters._low_enabled

    @property
    def _filter_high_enabled(self) -> bool:
        return self._filters._high_enabled

    @property
    def _filter_low_hz(self) -> float:
        return self._filters._low_hz

    @property
    def _filter_high_hz(self) -> float:
        return self._filters._high_hz

    def register_callback(self, event: str, callback: Callable) -> None:
        self._playback.register_callback(event, callback)

    # ---------- real-time callback ----------
    def _audio_callback(
        self,
        outdata: np.ndarray,
        frames: int,
        _time: Any,
        status: Any,
    ) -> None:
        if not self._playback._lock.acquire(blocking=False):
            outdata[:] = 0.0
            return

        try:
            if status:
                print(f"[AudioBackend] {status}")

            outdata[:] = 0.0

            if not self._playback._playing or self._playback._data is None:
                return

            # Handle Looping
            if self._loop_enabled and self._loop_provider:
                if self._active_loop_range is None:
                    self._active_loop_range = self._loop_provider(self._playback._cursor)

                lstart, lend = self._active_loop_range
                if self._playback._cursor >= lend - 0.001:
                    self._playback._cursor = lstart
                    self._read_sample_idx = int(self._playback._cursor * self._playback._sr)
                    self._processor.reset()
                    self.clear_tick_cache()

            to_read = 0
            if self._playback._speed == 1.0:
                start_idx = self._read_sample_idx
                end_idx = min(start_idx + frames, len(self._playback._data))
                to_read = end_idx - start_idx
                if to_read > 0:
                    chunk = self._playback._data[start_idx:end_idx]
                    chunk = self._filters.process(chunk)
                    outdata[:to_read, 0] = chunk * self._playback._volume
                    self._read_sample_idx = end_idx
            else:
                loops = 0
                while self._processor._tsm_buffer.available_read() < frames:
                    loops += 1
                    if loops > 100:
                        break

                    start_idx = self._read_sample_idx
                    if start_idx >= len(self._playback._data):
                        break

                    chunk_size = 16384
                    end_idx = min(start_idx + chunk_size, len(self._playback._data))
                    source_chunk = self._playback._data[start_idx:end_idx]
                    if source_chunk.size == 0:
                        break

                    self._read_sample_idx = end_idx
                    stretched = self._processor.process_stretch(source_chunk)
                    self._processor.apply_overlap_add(stretched)

                    if end_idx == len(self._playback._data):
                        break

                samples, to_read = self._processor._tsm_buffer.read(frames)
                samples = self._filters.process(samples)
                outdata[:, 0] = samples * self._playback._volume

            # Metronome
            self._metronome.add_clicks(outdata, frames, self._playback._cursor, self._subdivision_ticks_between)

            # Update cursor
            if to_read > 0:
                self._playback._cursor += (to_read / self._playback._sr) * self._playback._speed

            # EOF
            if to_read < frames and self._read_sample_idx >= len(self._playback._data):
                if self._processor._last_tsm_overlap is not None:
                    self._processor._tsm_buffer.write(self._processor._last_tsm_overlap)
                    self._processor._last_tsm_overlap = None

                if self._processor._tsm_buffer.available_read() == 0:
                    self._playback._playing = False
                    self._playback._cursor = 0.0
                    self._read_sample_idx = 0
                    self._processor.reset()
                    self._playback._on_finished()

        except Exception:
            traceback.print_exc()
        finally:
            self._playback._lock.release()
