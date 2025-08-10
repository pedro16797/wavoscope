"""
FFT spectrum widget with piano-key grid overlay.
Displays live spectrum and emits tone_requested(freq) when user clicks/drags.
"""
from __future__ import annotations

import numpy as np
from typing import Any

from PySide6.QtCore import QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QPolygonF
from PySide6.QtWidgets import QWidget

from wavoscope.utils.config import Config
from wavoscope.audio.spectrum_analyzer import analyze as run_fft

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
WHITE_KEYS = {0, 2, 4, 5, 7, 9, 11}


def _midi_to_freq(midi: int) -> float:
    """Convert MIDI note number to frequency (A4 = 69)."""
    return 440.0 * (2 ** ((midi - 69) / 12))


class SpectrumView(QWidget):
    # Public signals
    window_changed = Signal(float)   # FFT window duration changed
    tone_requested = Signal(float)   # Mouse press / drag

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumHeight(120)

        # Audio state
        self._y: np.ndarray | None = None
        self._sr: int = 44_100
        self._position: float = 0.0
        self._window: float = 0.3
        self._low_hz: float = _midi_to_freq(48)   # C2
        self._high_hz: float = _midi_to_freq(84)  # C5
        self._synth: Any = None

        # Mouse state
        self._pressed: bool = False

    # ---------- public API ----------
    def set_project(self, project):
        self.project = project
        self.set_audio_data(self.project._data, self.project._sr)

    def set_audio_data(self, y: np.ndarray, sr: int) -> None:
        self._y = y.astype(np.float32)
        self._sr = sr

    def set_position(self, sec: float) -> None:
        """Move vertical play-head and trigger repaint."""
        self._position = sec
        self.update()

    def set_fft_window(self, sec: float) -> None:
        self._window = max(sec, 0.05)
        self.window_changed.emit(self._window)
        self.update()

    def set_freq_range(self, low_hz: float, high_hz: float) -> None:
        """Update visible octave window."""
        self._low_hz = low_hz
        self._high_hz = high_hz
        self.update()

    def set_synth(self, synth: Any) -> None:
        self._synth = synth

    # ---------- helpers ----------
    def _hz_at_x(self, x: float) -> float:
        """Map pixel x-coordinate to frequency in Hz (log scale)."""
        span_log = np.log2(self._high_hz / self._low_hz)
        if span_log <= 0:
            return self._low_hz
        return self._low_hz * (2 ** (x * span_log / self.width()))

    # ---------- painting ----------
    def _on_theme_changed(self, name: str) -> None:
        from wavoscope.gui.colours import load_palette
        self.palette = load_palette(name)
        self.update()

    def paintEvent(self, _) -> None:
        if (self._y is None or
            not hasattr(self, '_low_hz') or
            self.width() <= 0):
            return

        freqs, db = run_fft(
            self._y, self._sr, self._position, self._window,
            self._low_hz, self._high_hz, self.width()
        )
        if freqs.size == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        h = self.height()
        span_log = max(np.log2(self._high_hz / self._low_hz), 1e-3)
        x_scale = self.width() / span_log

        # Piano-key grid
        first_midi = int(np.round(12 * np.log2(self._low_hz / 440) + 69))
        cfg = Config()
        visible_keys = int(cfg.get("ui.spectrum_keys", 37))
        for midi in range(first_midi, first_midi + visible_keys):
            hz = _midi_to_freq(midi)
            x = np.log2(hz / self._low_hz) * x_scale

            color = QColor(self.palette["keyWhite" if midi % 12 in WHITE_KEYS else "keyBlack"])
            color.setAlpha(128)
            painter.setPen(QPen(color, 3))
            painter.drawLine(int(x), 0, int(x), h)

            painter.setPen(QColor(self.palette["text"]))
            painter.drawText(int(x) + 2, 12, f"{NOTE_NAMES[midi % 12]}{(midi - 12) // 12}")

        # Spectrum line
        low_db, high_db = np.percentile(db, [1, 99])
        span_db = max(high_db - low_db, 1e-3)

        poly = QPolygonF()
        for f, d in zip(freqs, db):
            px = np.log2(f / self._low_hz) * x_scale
            py = h - ((d - low_db) / span_db) * h
            poly.append(QPointF(px, py))

        painter.setPen(QPen(QColor(self.palette["spectrum"]), 1))
        painter.drawPolyline(poly)
        painter.end()

    # ---------- mouse interaction ----------
    def mousePressEvent(self, event) -> None:
        self._pressed = True
        self._play_tone(event.position().x())

    def mouseMoveEvent(self, event) -> None:
        if self._pressed:
            self._play_tone(event.position().x())

    def mouseReleaseEvent(self, _) -> None:
        self._pressed = False
        if self._synth is not None:
            self._synth.stop_all()

    def leaveEvent(self, _) -> None:
        if self._synth is not None:
            self._synth.stop_all()

    # ---------- internal ----------
    def _play_tone(self, x: float) -> None:
        if self._synth is None:
            return
        hz = self._hz_at_x(x)
        if hz > 0:
            self._synth.stop_all()
            self._synth.start_tone(hz)