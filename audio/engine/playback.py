from __future__ import annotations
import threading
from typing import Callable, List, Dict, Any, Tuple
import numpy as np
from utils.logging import logger
try:
    import sounddevice as sd
except OSError:
    sd = None

class PlaybackEngine:
    def __init__(self, sr: int = 44100):
        self._sr = sr
        self._data: np.ndarray | None = None
        self._cursor: float = 0.0
        self._speed: float = 1.0
        self._volume: float = 1.0
        self._playing: bool = False
        self._lock = threading.RLock()
        self._stream: sd.OutputStream | None = None
        self._callbacks: Dict[str, List[Callable]] = {"finished": []}

    def set_data(self, data: np.ndarray, sr: int):
        with self._lock:
            self._data = data
            self._sr = sr
            self._cursor = 0.0
            self._playing = False

    def play(self):
        with self._lock:
            self._playing = True

    def pause(self):
        with self._lock:
            self._playing = False

    def seek(self, sec: float):
        with self._lock:
            duration = len(self._data) / self._sr if self._data is not None else 0.0
            self._cursor = max(0.0, min(sec, duration))

    def set_speed(self, speed: float):
        with self._lock:
            self._speed = max(0.1, min(speed, 4.0))

    def set_volume(self, vol: float):
        with self._lock:
            self._volume = max(0.0, min(vol, 1.0))

    def start_stream(self, callback: Callable):
        if sd is None:
            logger.warning("sounddevice not available.")
            return

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()

        self._stream = sd.OutputStream(
            samplerate=self._sr,
            channels=1,
            callback=callback,
            finished_callback=self._on_finished,
        )
        self._stream.start()

    def stop_stream(self):
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

    def _on_finished(self):
        for cb in self._callbacks.get("finished", []):
            cb()

    def register_callback(self, event: str, callback: Callable):
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    @property
    def position(self) -> float:
        return self._cursor

    @property
    def duration(self) -> float:
        return len(self._data) / self._sr if self._data is not None else 0.0
