"""
Thread-safe ring buffer for single-producer / single-consumer audio.
Uses an explicit count to resolve empty/full ambiguity.
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
        self._count: int = 0
        self._lock: threading.Lock = threading.Lock()

    # ---------- public ----------
    def write(self, data: np.ndarray) -> None:
        """Copy entire `data` into the ring (overwrites oldest if too large)."""
        with self._lock:
            n = data.size
            if n == 0:
                return

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

            self._write_idx = (self._write_idx + n) % self._size

            # Update count, clamping to size (since we overwrite)
            new_count = self._count + n
            if new_count > self._size:
                # We overwrote some unread data
                self._read_idx = self._write_idx
                self._count = self._size
            else:
                self._count = new_count

    def available_read(self) -> int:
        """Number of samples available to read."""
        with self._lock:
            return self._count

    def clear(self) -> None:
        """Reset read/write indices to zero."""
        with self._lock:
            self._write_idx = 0
            self._read_idx = 0
            self._count = 0
            self._buf.fill(0)

    def read(self, frames: int) -> np.ndarray:
        """Return exactly `frames` samples (silence if not enough available)."""
        with self._lock:
            if self._count < frames:
                return np.zeros(frames, dtype=np.float32)

            end = self._read_idx + frames
            if end <= self._size:
                out = self._buf[self._read_idx : end].copy()
            else:
                out = np.concatenate((self._buf[self._read_idx :], self._buf[: end - self._size]))

            self._read_idx = (self._read_idx + frames) % self._size
            self._count -= frames
            return out
