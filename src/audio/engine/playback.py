from __future__ import annotations
import threading
from typing import Callable, List, Dict
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
        self._device: int | str | None = None
        self._callbacks: Dict[str, List[Callable]] = {"finished": []}

        # "Playback finished" is signalled from the realtime audio callback but
        # dispatched on this worker thread. Finished callbacks may tear down the
        # stream or swap the active project, which must never happen on the
        # PortAudio callback thread (calling stop()/close() from within a stream's
        # own callback is undefined behaviour and can deadlock).
        self._finished_event = threading.Event()
        self._closed = threading.Event()
        self._dispatch_thread = threading.Thread(target=self._dispatch_finished, daemon=True)
        self._dispatch_thread.start()

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
            self._volume = max(0.0, min(vol, 4.0))

    def start_stream(self, callback: Callable):
        if sd is None:
            logger.warning("sounddevice not available.")
            return

        with self._lock:
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass

            try:
                self._stream = sd.OutputStream(
                    samplerate=self._sr,
                    channels=1,
                    callback=callback,
                    device=self._device,
                )
                self._stream.start()
            except Exception as e:
                logger.error(f"Failed to start audio stream on device {self._device}: {e}")
                self._stream = None

    def stop_stream(self):
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

    def close(self):
        """Stop the stream and the finished-dispatch worker.

        Safe to call from a finished callback (i.e. from the dispatch thread):
        it signals the worker to exit rather than joining it.
        """
        self.stop_stream()
        self._closed.set()
        self._finished_event.set()  # wake the worker so it observes _closed and exits

    def notify_finished(self):
        """Signal that playback reached the end. Safe to call from the audio callback."""
        self._finished_event.set()

    def _dispatch_finished(self):
        while True:
            self._finished_event.wait()
            self._finished_event.clear()
            if self._closed.is_set():
                return
            for cb in list(self._callbacks.get("finished", [])):
                try:
                    cb()
                except Exception:
                    logger.exception("Error in playback-finished callback")

    def register_callback(self, event: str, callback: Callable):
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    @property
    def position(self) -> float:
        return self._cursor

    @property
    def duration(self) -> float:
        return len(self._data) / self._sr if self._data is not None else 0.0
