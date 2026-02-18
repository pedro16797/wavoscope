from __future__ import annotations
from typing import Any
from utils.logging import logger
import numpy as np
import python_stretch.Signalsmith as ps
from audio.ringbuffer import RingBuffer

class AudioProcessor:
    def __init__(self, sr: int):
        self._sr = sr
        self._stretcher = ps.Stretch()
        self._stretcher.preset(1, float(sr))
        self._tsm_buffer = RingBuffer(sr * 10)
        self._last_tsm_overlap: np.ndarray | None = None
        self._novasr_enabled: bool = False
        self._novasr: Any = None

    def reset(self, sr: int | None = None, speed: float = 1.0):
        if sr is not None:
            self._sr = sr
            self._stretcher = ps.Stretch()
            self._stretcher.preset(1, float(self._sr))
            self._stretcher.setTimeFactor(speed)
            self._tsm_buffer = RingBuffer(int(self._sr * 10))
        else:
            self._stretcher.reset()
            self._tsm_buffer.clear()
        self._last_tsm_overlap = None
        if self._novasr:
            self._novasr.reset()

    def set_speed(self, speed: float):
        self._stretcher.setTimeFactor(speed)
        self._tsm_buffer.clear()
        self._last_tsm_overlap = None

    def set_novasr_enabled(self, enabled: bool):
        self._novasr_enabled = enabled
        if enabled and self._novasr is None:
            try:
                from audio.novasr import NovaSR
                self._novasr = NovaSR()
            except Exception:
                logger.exception("Failed to load NovaSR")
                self._novasr_enabled = False

    def process_stretch(self, chunk: np.ndarray) -> np.ndarray:
        stretched = self._stretcher.process(chunk.reshape(1, -1)).flatten()
        if self._novasr_enabled and self._novasr is not None:
            stretched = self._novasr.enhance(stretched, self._sr)
        return stretched

    def apply_overlap_add(self, stretched: np.ndarray):
        if stretched.size == 0:
            return

        overlap_size = 512
        if self._last_tsm_overlap is not None:
            actual_overlap = min(overlap_size, stretched.size)
            fade_out = np.linspace(1, 0, actual_overlap, dtype=np.float32)
            fade_in = np.linspace(0, 1, actual_overlap, dtype=np.float32)

            blended = (
                stretched[:actual_overlap] * fade_in +
                self._last_tsm_overlap[:actual_overlap] * fade_out
            )
            self._tsm_buffer.write(blended)

            if stretched.size > overlap_size:
                main_part = stretched[overlap_size:-overlap_size]
                if main_part.size > 0:
                    self._tsm_buffer.write(main_part)
                self._last_tsm_overlap = stretched[-overlap_size:].copy()
            else:
                self._last_tsm_overlap = None
        else:
            if stretched.size > overlap_size:
                self._tsm_buffer.write(stretched[:-overlap_size])
                self._last_tsm_overlap = stretched[-overlap_size:].copy()
            else:
                self._tsm_buffer.write(stretched)
                self._last_tsm_overlap = None
