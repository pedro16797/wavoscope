"""
Core playback engine: file I/O, speed control, metronome clicks, real-time stream.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, List, Tuple, Any, Dict

import numpy as np
import soundfile as sf

from session.looping import LoopingEngine
from audio.synth import SimpleSynth
from audio.engine.playback import PlaybackEngine
from audio.engine.processing import AudioProcessor
from audio.engine.metronome import MetronomeEngine
from audio.engine.filters import FilterEngine
from utils.logging import logger


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

        # Device management
        self._selected_device_name: str | None = None  # None means "System Default"
        self._last_default_name: str | None = None
        self._watcher_thread: threading.Thread | None = None
        self._start_watcher()

        # Looping state
        self._loop_enabled: bool = False
        self._active_loop_range: Tuple[float, float] | None = None

        # Project data cache for thread-safety and performance
        self._cached_flags: List[Dict[str, Any]] = []
        self._cached_lyrics: List[Dict[str, Any]] = []
        self._cached_loop_mode: str = "none"
        self._cached_selected_lyric_idx: int | None = None
        self._cached_duration: float = 0.0

    # ---------- file I/O ----------
    def open_file(self, path: Path) -> None:
        """Load audio file, reset playback state."""
        with self._playback._lock:
            data, sr = sf.read(str(path), always_2d=False, dtype="float32")
            if data.ndim > 1:
                data = data.mean(axis=1)
            data = data.astype(np.float32)

            self._playback.set_data(data, sr)
            self._processor.reset(sr, speed=self._playback._speed)
            self._metronome.set_sr(sr)
            self._filters.set_sr(sr)

            self._read_sample_idx = 0
            self._stop_event.clear()

            self._playback.start_stream(self._audio_callback)

    def close(self) -> None:
        """Stop stream and release resources."""
        self._stop_event.set()
        if self._watcher_thread:
            self._watcher_thread.join(timeout=1.0)
        self._playback.stop_stream()
        self._synth.close()

    # ---------- hardware management ----------
    @staticmethod
    def list_devices() -> List[Dict[str, Any]]:
        """List available output devices."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            output_devices = []
            for i, d in enumerate(devices):
                if d['max_output_channels'] > 0:
                    output_devices.append({
                        "index": i,
                        "name": d['name'],
                        "hostapi": d['hostapi'],
                        "is_default": i == sd.default.device[1]
                    })
            return output_devices
        except Exception:
            return []

    def set_device(self, device_name: str | None) -> None:
        """Set the active output device by name. None means 'System Default'."""
        self._selected_device_name = device_name
        self._update_hardware_device()

    def _update_hardware_device(self) -> None:
        try:
            import sounddevice as sd
            device_idx = None
            if self._selected_device_name:
                devices = sd.query_devices()
                for i, d in enumerate(devices):
                    if d['name'] == self._selected_device_name and d['max_output_channels'] > 0:
                        device_idx = i
                        break

            self._playback._device = device_idx
            self._synth.set_device(device_idx)

            # If we're already playing or a file is open, we should restart the playback stream
            if self._playback._data is not None:
                self._playback.start_stream(self._audio_callback)
        except Exception as e:
            logger.error(f"Error updating audio device: {e}")

    def _start_watcher(self) -> None:
        self._watcher_thread = threading.Thread(target=self._watch_devices, daemon=True)
        self._watcher_thread.start()

    def _watch_devices(self) -> None:
        import time
        while not self._stop_event.is_set():
            if self._selected_device_name is None:
                try:
                    import sounddevice as sd
                    devices = sd.query_devices()
                    def_idx = sd.default.device[1]
                    if def_idx >= 0:
                        curr_name = devices[def_idx]['name']
                        if self._last_default_name is not None and curr_name != self._last_default_name:
                            logger.info(f"Default audio device changed to {curr_name}. Updating streams.")
                            self._update_hardware_device()
                        self._last_default_name = curr_name
                except Exception:
                    pass
            time.sleep(2.0)

    # ---------- playback control ----------
    def seek(self, sec: float) -> None:
        with self._playback._lock:
            self._playback.seek(sec)

            # Only reset loop range if we seek past the current loop
            if self._active_loop_range:
                _, lend = self._active_loop_range
                if sec >= lend:
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

    def set_click_volume(self, volume: float) -> None:
        self._metronome.set_volume(volume)

    def sync_project_data(self, flags: List[Dict[str, Any]], lyrics: List[Dict[str, Any]], loop_mode: str, selected_lyric_idx: int | None, duration: float) -> None:
        with self._playback._lock:
            self._cached_flags = flags
            self._cached_lyrics = lyrics
            self._cached_loop_mode = loop_mode
            self._cached_selected_lyric_idx = selected_lyric_idx
            self._cached_duration = duration

    def set_loop_enabled(self, enabled: bool) -> None:
        with self._playback._lock:
            self._loop_enabled = enabled
            if not enabled:
                self._active_loop_range = None

    def set_filter(self, **kwargs) -> None:
        with self._playback._lock:
            self._filters.set_filter(**kwargs)

    def reset_loop_range(self) -> None:
        with self._playback._lock:
            self._active_loop_range = None

    def clear_tick_cache(self) -> None:
        if hasattr(self, "_last_tick_time"):
            delattr(self, "_last_tick_time")
        self._metronome.reset()

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

    @property
    def active_loop_range(self) -> Tuple[float, float] | None:
        with self._playback._lock:
            return self._active_loop_range

    def register_callback(self, event: str, callback: Callable) -> None:
        self._playback.register_callback(event, callback)

    def _calculate_subdivision_ticks(self, start: float, end: float) -> list[tuple[float, bool]]:
        """Replacement for Project.subdivision_ticks_between using cached data."""
        ticks: list[tuple[float, bool]] = []
        flags = self._cached_flags

        for i, prev in enumerate(flags):
            if prev.get("type", "rhythm") != "rhythm":
                continue
            if start <= prev["t"] < end:
                ticks.append((prev["t"], True))
            if i + 1 < len(flags):
                nxt = flags[i + 1]
                subdiv = prev.get("div", 0)
                if subdiv == 0:
                    for p in reversed(flags[: i + 1]):
                        if p.get("type", "rhythm") == "rhythm" and p.get("div", 0) != 0:
                            subdiv = p["div"]
                            break
                    else:
                        subdiv = 1
                if subdiv > 1:
                    span = nxt["t"] - prev["t"]
                    step = span / subdiv
                    for k in range(1, subdiv):
                        tick_time = prev["t"] + k * step
                        if start <= tick_time < end:
                            ticks.append((tick_time, False))
        return sorted(ticks, key=lambda t: t[0])

    # ---------- real-time callback ----------
    def _audio_callback(
        self,
        outdata: np.ndarray,
        frames: int,
        _time: Any,
        status: Any,
    ) -> None:
        outdata[:] = 0.0
        if not self._playback._lock.acquire(blocking=False):
            return

        try:
            outdata[:] = 0.0

            if not self._playback._playing or self._playback._data is None:
                return

            # Handle Looping
            if self._loop_enabled:
                if self._active_loop_range is None:
                    engine = LoopingEngine()
                    engine.set_loop_mode(self._cached_loop_mode)
                    self._active_loop_range = engine.get_loop_range(
                        self._playback._cursor,
                        self._cached_duration,
                        self._cached_flags,
                        self._cached_lyrics,
                        self._cached_selected_lyric_idx
                    )

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
            self._metronome.add_clicks(
                outdata,
                to_read,
                self._playback._cursor,
                self._calculate_subdivision_ticks,
                self._playback._speed
            )

            # Update cursor
            if to_read > 0:
                self._playback._cursor += (to_read / self._playback._sr) * self._playback._speed

            # EOF
            if to_read < frames and self._read_sample_idx >= len(self._playback._data):
                if self._processor._last_tsm_overlap is not None:
                    self._processor._tsm_buffer.write(self._processor._last_tsm_overlap)
                    self._processor._last_tsm_overlap = None

                if self._processor._tsm_buffer.available_read() == 0:
                    if self._loop_enabled:
                        if self._active_loop_range is None:
                            engine = LoopingEngine()
                            engine.set_loop_mode(self._cached_loop_mode)
                            self._active_loop_range = engine.get_loop_range(
                                self._playback._cursor,
                                self._cached_duration,
                                self._cached_flags,
                                self._cached_lyrics,
                                self._cached_selected_lyric_idx
                            )
                        lstart, _ = self._active_loop_range
                        self._playback._cursor = lstart
                        self._read_sample_idx = int(self._playback._cursor * self._playback._sr)
                        self._processor.reset()
                        self.clear_tick_cache()
                    else:
                        self._playback._playing = False
                        self._playback._cursor = 0.0
                        self._read_sample_idx = 0
                        self._processor.reset()
                        self._playback._on_finished()

        except Exception:
            logger.exception("Error in audio callback")
        finally:
            self._playback._lock.release()
