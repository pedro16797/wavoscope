"""
Core playback engine: file I/O, speed control, metronome clicks, real-time stream.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, List, Tuple, Any, Dict
import bisect
import traceback

import numpy as np
import python_stretch.Signalsmith as ps
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

        self._stretcher = ps.Stretch()
        self._stretcher.preset(1, float(self._sr))
        self._stretcher.setTimeFactor(self._speed)

        # 10s safety to handle slow speeds (0.1x) with large chunks
        self._tsm_buffer = RingBuffer(self._sr * 10)
        self._read_sample_idx: int = 0
        self._last_tsm_overlap: np.ndarray | None = None

        self._novasr_enabled: bool = False
        self._novasr: Any = None

        self._synth = SimpleSynth(self._sr)

        self._stream: sd.OutputStream | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        # Metronome state
        self._click_volume: float = 0.3
        self._strong_freq: float = 1_200.0
        self._weak_freq: float = 800.0
        self._metronome_enabled: bool = True

        # Filter state
        self._filter_enabled: bool = False
        self._filter_low_enabled: bool = True
        self._filter_high_enabled: bool = True
        self._filter_low_hz: float = 200.0
        self._filter_high_hz: float = 2000.0
        self._filter_sos: np.ndarray | None = None
        self._filter_zi: np.ndarray | None = None

        # Looping state
        self._loop_enabled: bool = False
        self._loop_provider: Callable[[float], Tuple[float, float]] | None = None
        self._active_loop_range: Tuple[float, float] | None = None

        self._subdivision_ticks_between: Callable[[float, float], List[Tuple[float, bool]]] | None = None

        # Pre-calculated click waveforms
        self._strong_click: np.ndarray = np.zeros(0, dtype=np.float32)
        self._weak_click: np.ndarray = np.zeros(0, dtype=np.float32)
        self._precalculate_clicks()
        self._update_filter_coeffs()

    # ---------- file I/O ----------
    def open_file(self, path: Path) -> None:
        """Load audio file, reset playback state."""
        with self._lock:
            data, sr = sf.read(str(path), always_2d=False, dtype="float32")
            if data.ndim > 1:
                data = data.mean(axis=1)
            self._data = data.astype(np.float32)
            self._sr = sr
            self._update_filter_coeffs()
            self._cursor = 0.0
            self._read_sample_idx = 0
            self._playing = False
            self._stop_event.clear()

            # Update stretcher for new sample rate
            self._stretcher = ps.Stretch()
            self._stretcher.preset(1, float(self._sr))
            self._stretcher.setTimeFactor(self._speed)
            self._tsm_buffer = RingBuffer(int(self._sr * 10))
            self._last_tsm_overlap = None

            if self._novasr:
                self._novasr.reset()

            self._start_stream()

    def close(self) -> None:
        """Stop stream and release resources."""
        with self._lock:
            self._stop_event.set()
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if self._synth is not None:
                self._synth.close()

    # ---------- playback control ----------
    def seek(self, sec: float) -> None:
        with self._lock:
            self._cursor = max(0.0, min(sec, self.duration))
            self._active_loop_range = None
            if self._filter_sos is not None:
                self._filter_zi = scipy.signal.sosfilt_zi(self._filter_sos)

            self._read_sample_idx = int(self._cursor * self._sr)
            self._tsm_buffer.clear()
            self._last_tsm_overlap = None
            self._stretcher.reset()
            if self._novasr is not None:
                self._novasr.reset()
            self.clear_tick_cache()

    def play(self) -> None:
        with self._lock:
            self._playing = True

    def pause(self) -> None:
        with self._lock:
            self._playing = False
            # We DON'T clear the buffer or reset the stretcher here,
            # so we can resume seamlessly.
            self.clear_tick_cache()

    def set_speed(self, speed: float) -> None:
        with self._lock:
            self._speed = max(0.1, min(speed, 4.0))
            self._stretcher.setTimeFactor(self._speed)
            # Clear buffer so speed change is immediate
            self._tsm_buffer.clear()
            self._last_tsm_overlap = None
            # Re-sync read index to current cursor to prevent jumps when switching modes
            self._read_sample_idx = int(self._cursor * self._sr)

    def set_volume(self, vol: float) -> None:
        with self._lock:
            self._volume = max(0.0, min(vol, 1.0))

    def set_metronome_enabled(self, enabled: bool) -> None:
        self._metronome_enabled = enabled

    def set_novasr_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._novasr_enabled = enabled
            if enabled and self._novasr is None:
                try:
                    from audio.novasr import NovaSR
                    self._novasr = NovaSR()
                except Exception:
                    traceback.print_exc()
                    self._novasr_enabled = False

    def set_click_gain(self, gain: float) -> None:
        # Keep this method name for compatibility with Project, but update internal field
        self._click_volume = max(0.0, min(gain, 1.0))
        self._precalculate_clicks()

    def set_tick_provider(self, fn: Callable[[float, float], list[tuple[float, bool]]]) -> None:
        """Inject Project.subdivision_ticks_between for metronome clicks."""
        self._subdivision_ticks_between = fn

    def set_loop_provider(self, fn: Callable[[float], Tuple[float, float]]) -> None:
        """Inject Project.get_loop_range."""
        self._loop_provider = fn

    def set_loop_enabled(self, enabled: bool) -> None:
        self._loop_enabled = enabled
        if not enabled:
            self._active_loop_range = None

    def set_filter(self,
                   enabled: bool | None = None,
                   low: float | None = None,
                   high: float | None = None,
                   low_enabled: bool | None = None,
                   high_enabled: bool | None = None) -> None:
        """Update filter settings."""
        with self._lock:
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
        if not self._filter_enabled or (not self._filter_low_enabled and not self._filter_high_enabled):
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
        if not self._lock.acquire(blocking=False):
            # If we can't get the lock immediately, play silence to avoid glitching
            outdata[:] = 0.0
            return

        try:
            if status:
                print(f"[AudioBackend] {status}")

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
                    self._read_sample_idx = int(self._cursor * self._sr)
                    self._tsm_buffer.clear()
                    self._last_tsm_overlap = None
                    self.clear_tick_cache()

            to_read = 0
            if self._speed == 1.0:
                # 1. Bypass Mode: read directly from source for zero-latency, zero-artifact playback
                start_idx = self._read_sample_idx
                end_idx = min(start_idx + frames, len(self._data))
                to_read = end_idx - start_idx
                if to_read > 0:
                    chunk = self._data[start_idx:end_idx]

                    # Band-pass filter
                    if self._filter_enabled and self._filter_sos is not None:
                        chunk, self._filter_zi = scipy.signal.sosfilt(self._filter_sos, chunk, zi=self._filter_zi)

                    outdata[:to_read, 0] = chunk * self._volume
                    self._read_sample_idx = end_idx
            else:
                # 2. TSM / Enhancement Mode
                # Fill TSM buffer
                loops = 0
                while self._tsm_buffer.available_read() < frames:
                    loops += 1
                    if loops > 100: # Safety
                        break

                    start_idx = self._read_sample_idx
                    if start_idx >= len(self._data):
                        break

                    # Use a larger chunk size for TSM stability
                    chunk_size = 16384
                    end_idx = min(start_idx + chunk_size, len(self._data))
                    source_chunk = self._data[start_idx:end_idx]
                    if source_chunk.size == 0:
                        break

                    self._read_sample_idx = end_idx

                    # Stretch
                    stretched = self._stretcher.process(source_chunk.reshape(1, -1)).flatten()

                    # NovaSR enhancement
                    if self._novasr_enabled and self._novasr is not None:
                        stretched = self._novasr.enhance(stretched, self._sr)

                    if stretched.size > 0:
                        overlap_size = 512
                        if self._last_tsm_overlap is not None:
                            # Cross-fade previous tail with current head
                            actual_overlap = min(overlap_size, stretched.size)
                            fade_out = np.linspace(1, 0, actual_overlap, dtype=np.float32)
                            fade_in = np.linspace(0, 1, actual_overlap, dtype=np.float32)

                            blended = (
                                stretched[:actual_overlap] * fade_in +
                                self._last_tsm_overlap[:actual_overlap] * fade_out
                            )
                            self._tsm_buffer.write(blended)

                            # Write the rest of the current chunk, keeping a new tail
                            if stretched.size > overlap_size:
                                main_part = stretched[overlap_size:-overlap_size]
                                if main_part.size > 0:
                                    self._tsm_buffer.write(main_part)
                                self._last_tsm_overlap = stretched[-overlap_size:].copy()
                            else:
                                self._last_tsm_overlap = None # Current chunk was too small to have a new tail
                        else:
                            # No previous tail, write everything but the tail
                            if stretched.size > overlap_size:
                                self._tsm_buffer.write(stretched[:-overlap_size])
                                self._last_tsm_overlap = stretched[-overlap_size:].copy()
                            else:
                                # Too small even for a tail, just write it and don't start a tail
                                self._tsm_buffer.write(stretched)
                                self._last_tsm_overlap = None

                    if end_idx == len(self._data):
                        break

                # Read from TSM buffer
                samples, to_read = self._tsm_buffer.read(frames)

                # Band-pass filter
                if self._filter_enabled and self._filter_sos is not None:
                    samples, self._filter_zi = scipy.signal.sosfilt(self._filter_sos, samples, zi=self._filter_zi)

                outdata[:, 0] = samples * self._volume

            # 3. Metronome overlay
            if self._metronome_enabled and self._subdivision_ticks_between:
                self._add_metronome_clicks(outdata, frames)

            # 4. Update playback cursor based on actual samples read
            if to_read > 0:
                self._cursor += (to_read / self._sr) * self._speed

            # 5. Check for EOF
            if to_read < frames and self._read_sample_idx >= len(self._data):
                # Flush any remaining tail
                if self._last_tsm_overlap is not None:
                    self._tsm_buffer.write(self._last_tsm_overlap)
                    self._last_tsm_overlap = None

                # Check if we still have nothing to read after flush
                if self._tsm_buffer.available_read() == 0:
                    self._playing = False
                    self._cursor = 0.0
                    self._read_sample_idx = 0
                    self._tsm_buffer.clear()
                    self._stretcher.reset()
                    if self._novasr is not None:
                        self._novasr.reset()
                    self._emit("finished")

        except Exception:
            traceback.print_exc()
        finally:
            self._lock.release()

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

            volume = self._click_volume * (0.5 if shaded else 1.0)
            click_src = self._strong_click if is_strong else self._weak_click

            click_dur = min(len(click_src), frames - offset)
            if click_dur > 0:
                outdata[offset : offset + click_dur, 0] += click_src[:click_dur] * volume
