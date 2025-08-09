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
        self._metronome_enabled = True

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
    def seek(self, sec: float):
        self._cursor = max(0.0, min(sec, self.duration))
        self._last_processed_tick = None
        
    def play(self):
        self._playing = True
        
    def pause(self):
        self._playing = False
        self._last_processed_tick = None

    def set_speed(self, speed: float):
        self._speed = max(0.1, min(1.0, speed))

    def set_volume(self, vol: float):
        self._volume = max(0.0, min(1.0, vol))

    def set_tick_provider(self, fn):
        self._subdivision_ticks_between = fn

    def _make_click(self, frames, freq):
        t = np.arange(frames) / self._sr
        envelope = np.exp(-t * 40)
        wave = 4* np.sin(2 * np.pi * freq * t) * envelope
        return wave.astype(np.float32)
    
    def set_metronome_enabled(self, enabled: bool):
        self._metronome_enabled = enabled

    def is_metronome_enabled(self) -> bool:
        return self._metronome_enabled

    def clear_tick_cache(self):
        if hasattr(self, '_last_tick_time'):
            delattr(self, '_last_tick_time')

    def set_click_gain(self, gain: float):
        self._click_gain = max(0.0, min(1.0, gain))

    def get_click_gain(self) -> float:
        return self._click_gain

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
        
        # Always start with silence
        outdata[:] = 0
        
        if not self._playing or self._data is None:
            return

        # compute required samples
        needed = int(frames * self._speed)
        start = int(self._cursor * self._sr)
        end   = int((self._cursor + frames / self._speed) * self._sr)
        
        # Prevent access beyond data bounds
        actual_end = min(end, len(self._data))
        actual_start = min(start, actual_end)
        
        chunk = self._data[actual_start:actual_end]

        if len(chunk) < needed:          # EOF
            padding = needed - len(chunk)
            chunk = np.concatenate([chunk, np.zeros(padding, dtype=np.float32)])
            self._cursor = 0.0
            self._playing = False
            self.finished.emit()
        elif len(chunk) > needed:
            chunk = chunk[:needed]

        # Ensure exactly 'frames' samples
        if len(chunk) < frames:
            chunk = np.concatenate([chunk, np.zeros(frames - len(chunk), dtype=np.float32)])
        elif len(chunk) > frames:
            chunk = chunk[:frames]

        # filter for speed changes
        if self._speed < 0.9:
            low = 100 + (1 - self._speed) * 80
            high = 20000 - (1 - self._speed) * 16000
            sos = butter(2, [low, high], btype='band', fs=self._sr, output='sos')
            chunk = sosfilt(sos, chunk)

        # Apply volume and send to output
        outdata[:, 0] = chunk * self._volume

        # Add metronome clicks if enabled
        if self._metronome_enabled:
            self._add_metronome_clicks(outdata, frames)
            
        self._cursor += frames / self._sr * self._speed

    def _add_metronome_clicks(self, outdata, frames):
        if not hasattr(self, '_subdivision_ticks_between') or not self._subdivision_ticks_between:
            return
            
        callback_start = self._cursor
        callback_end = self._cursor + frames / self._sr
        
        ticks = self._subdivision_ticks_between(callback_start, callback_end)
        
        for tick_time, is_strong in ticks:
            if tick_time < callback_start or tick_time >= callback_end:
                continue
                
            buffer_offset = int((tick_time - callback_start) * self._sr)
            
            if 0 <= buffer_offset < frames:
                click_duration = min(int(0.1 * self._sr), frames - buffer_offset)
                
                if click_duration > 0:
                    t = np.arange(click_duration) / self._sr
                    envelope = np.exp(-t * 10)
                    strong_freq = 800
                    weak_freq = 1200
                    freq = strong_freq if is_strong else weak_freq
                    base_gain = self._click_gain
                    
                    # Add second harmonic for more presence
                    fundamental = np.sin(2 * np.pi * freq * t)
                    harmonic = 0.3 * np.sin(2 * np.pi * freq * 2 * t)
                    click_samples = (fundamental + harmonic) * envelope * base_gain
                    click_samples = np.clip(click_samples, -0.8, 0.8)
                    
                    outdata[buffer_offset:buffer_offset + click_duration, 0] += click_samples