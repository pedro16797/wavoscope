"""
Thread-safe lock-free ring buffer for single-producer / single-consumer audio.

Buffer always returns float32 silence instead of underrunning.
"""
from __future__ import annotations

import threading
from typing import Final

import numpy as np


class RingBuffer:
    """Circular float32 buffer with lock and contiguous read/write."""

    def __init__(self, size: int) -> None:
        self._size: Final[int] = size
        self._buf: np.ndarray = np.zeros(size, dtype=np.float32)
        self._write_idx: int = 0
        self._read_idx: int = 0
        self._lock: threading.Lock = threading.Lock()

    # ---------- public ----------
    def write(self, data: np.ndarray) -> None:
        """Copy entire `data` into the ring (overwrites oldest if too large)."""
        with self._lock:
            n = data.size
            if n > self._size:
                data = data[-self._size :]
                n = self._size

            end = self._write_idx + n
            if end <= self._size:
                self._buf[self._write_idx : end] = data
            else:
                split = self._size - self._write_idx
                self._buf[self._write_idx :] = data[:split]
                self._buf[: end - self._size] = data[split:]
            self._write_idx = end % self._size

    def read(self, frames: int) -> np.ndarray:
        """Return exactly `frames` samples (silence if not enough available)."""
        with self._lock:
            avail = (self._write_idx - self._read_idx) % self._size
            if avail < frames:
                return np.zeros(frames, dtype=np.float32)

            end = self._read_idx + frames
            if end <= self._size:
                out = self._buf[self._read_idx : end].copy()
            else:
                out = np.concatenate((self._buf[self._read_idx :], self._buf[: end - self._size]))
            self._read_idx = end % self._size
            return out