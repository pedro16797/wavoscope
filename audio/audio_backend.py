import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from scipy.signal import butter, sosfilt
from PySide6.QtCore import Signal
from wavoscope.audio.ringbuffer import RingBuffer
from wavoscope.audio.synth import SimpleSynth

class AudioBackend:
    finished = Signal()

    def __init__(self):
        self._data = None          # mono float32
        self._sr = 44100
        self._cursor = 0.0
        self._speed = 1.0
        self._volume = 1.0
        self._playing = False
        self._output_buffer = RingBuffer(2 * 44100)  # 2 s safety
        self._synth = SimpleSynth()
        self._stream = None
        self._thread = None
        self._stop_event = threading.Event()
        self._click_gain = 0.3
        self._strong_freq = 1200
        self._weak_freq   = 800

    # ---------- File I/O ----------
    def open_file(self, path: Path):
        data, sr = sf.read(str(path), always_2d=False, dtype='float32')
        if data.ndim > 1:
            data = data.mean(axis=1)
        self._data = data.astype(np.float32)
        self._sr = sr
        self._cursor = 0.0
        self._playing = False
        self._stop_event.clear()
        self._start_stream()

    def _on_finished(self):
        pass

    def close(self):
        self._stop_event.set()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _start_stream(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
        self._stream = sd.OutputStream(
            samplerate=self._sr,
            channels=1,
            callback=self._audio_callback,
            finished_callback=self._on_finished
        )
        self._stream.start()

    # ---------- Playback control ----------
    def play(self):
        self._playing = True

    def pause(self):
        self._playing = False

    def seek(self, sec: float):
        self._cursor = max(0.0, min(sec, self.duration))

    def set_speed(self, speed: float):
        self._speed = max(0.1, min(1.0, speed))

    def set_volume(self, vol: float):
        self._volume = max(0.0, min(1.0, vol))

    def set_tick_provider(self, fn):
        self._subdivision_ticks_between = fn

    def _make_click(self, frames, freq):
        t = np.arange(frames) / self._sr
        envelope = np.exp(-t * 40)
        wave = np.sin(2 * np.pi * freq * t) * envelope
        return wave.astype(np.float32)

    @property
    def position(self):
        return self._cursor

    @property
    def duration(self):
        return len(self._data) / self._sr if self._data is not None else 0.0

    # ---------- Internal audio thread ----------
    def _audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)
        if not self._playing or self._data is None:
            outdata[:] = 0
            return

        # compute required samples
        needed = int(frames * self._speed)
        start = int(self._cursor * self._sr)
        end   = int((self._cursor + frames / self._speed) * self._sr)
        chunk = self._data[start:end]

        if len(chunk) < needed:          # EOF
            padding = needed - len(chunk)
            chunk = np.concatenate([chunk, np.zeros(padding, dtype=np.float32)])
            self._cursor = 0.0
            self._playing = False
            self.finished.emit()

        # resize to exact frame count
        if len(chunk) < frames:
            chunk = np.concatenate([chunk, np.zeros(frames - len(chunk), dtype=np.float32)])
        elif len(chunk) > frames:
            chunk = chunk[:frames]

        # filter, volume & output
        if self._speed < 0.9:
            # based on speed lerp between 100 and 20 for low, and 20000 and 4000 for high
            low = 100 + (1 - self._speed) * 80
            high = 20000 - (1 - self._speed) * 16000
            sos = butter(2, [low, high], btype='band', fs=self._sr, output='sos')
            chunk = sosfilt(sos, chunk)

        # metronome clicks
        if self._playing:
            look_ahead = frames / self._sr
            if hasattr(self, '_subdivision_ticks_between') and self._subdivision_ticks_between:
                ticks = self._subdivision_ticks_between(self._cursor,
                                                        self._cursor + look_ahead)
                for tick_t, is_strong in ticks:
                    offset_frames = int((tick_t - self._cursor) * self._sr)
                    if 0 <= offset_frames < len(chunk):
                        freq = self._strong_freq if is_strong else self._weak_freq
                        click = self._make_click(len(chunk) - offset_frames, freq)
                        chunk[offset_frames:] += click * self._click_gain

        outdata[:, 0] = chunk * self._volume
        self._cursor += frames / self._sr * self._speed