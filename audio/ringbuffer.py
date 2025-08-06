import numpy as np
import threading

class RingBuffer:
    def __init__(self, size: int):
        self._buf = np.zeros(size, dtype=np.float32)
        self._size = size
        self._w = 0
        self._r = 0
        self._lock = threading.Lock()

    def write(self, data: np.ndarray):
        with self._lock:
            n = len(data)
            if n > self._size:
                data = data[-self._size:]
                n = self._size
            end = self._w + n
            if end <= self._size:
                self._buf[self._w:end] = data
            else:
                split = self._size - self._w
                self._buf[self._w:] = data[:split]
                self._buf[:end - self._size] = data[split:]
            self._w = end % self._size

    def read(self, frames: int) -> np.ndarray:
        with self._lock:
            avail = (self._w - self._r) % self._size
            if avail < frames:
                return np.zeros(frames, dtype=np.float32)
            end = self._r + frames
            if end <= self._size:
                out = self._buf[self._r:end].copy()
            else:
                out = np.concatenate((self._buf[self._r:], self._buf[:end - self._size]))
            self._r = end % self._size
            return out