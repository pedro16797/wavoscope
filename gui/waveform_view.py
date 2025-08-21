"""
Scrollable and zoomable waveform view that displays audio bars and a play-head.

Public signals
--------------
seek_requested(float)   – user clicked to seek
viewport_changed        – zoom/pan changed
"""
from __future__ import annotations

import numpy as np
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QWidget

if TYPE_CHECKING:
    from wavoscope.session.project import Project


class WaveformView(QGraphicsView):
    # Public API
    seek_requested = Signal(float)
    stop_origin_changed = Signal(float)
    viewport_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)

        # Audio state
        self.project: Project | None = None
        self._y: np.ndarray | None = None
        self._sr: int = 44_100
        self._duration: float = 0.0

        # Viewport state
        self._offset: float = 0.0  # seconds at left edge
        self._zoom: float = 1.0    # pixels / sample
        self._cursor: float = 0.0  # play-head time (seconds)

        # Mouse drag state
        self._drag_threshold: int = 10  # px
        self._drag_active: bool = False
        self._drag_origin: QPointF | None = None

        # De-bounced redraw
        self._redraw_timer = QTimer(self)
        self._redraw_timer.setSingleShot(True)
        self._redraw_timer.setInterval(50)
        self._redraw_timer.timeout.connect(self._redraw)

    # ---------- public ----------
    def set_project(self, project: Project) -> None:
        self.project = project
        self.set_audio_data(project._data, project._sr)
        self.set_viewport_range(0.0, project.duration)

    def set_audio_data(self, y: np.ndarray, sr: int) -> None:
        self._y = y.astype(np.float32)
        self._sr = sr
        self._duration = len(y) / sr

    def set_viewport_range(self, start_sec: float, end_sec: float) -> None:
        """Zoom/pan to show exactly [start_sec, end_sec]."""
        self._offset = start_sec
        self._zoom = self.width() / max((end_sec - start_sec) * self._sr, 1e-6)
        self._redraw()
        self.viewport_changed.emit()

    def set_cursor(self, sec: float) -> None:
        """Update the vertical play-head line."""
        self._cursor = sec
        self.viewport().update()

    # ---------- drawing ----------
    def _on_theme_changed(self, name: str) -> None:
        from wavoscope.gui.colours import load_palette
        self.palette = load_palette(name)
        self._redraw()

    def _redraw(self) -> None:
        """Re-populate the scene with fresh bars."""
        if (
            self.project is None
            or self.project.wave_cache is None
            or self.width() <= 0
            or self._zoom <= 0
        ):
            self.scene().clear()
            return

        width_px = self.width()
        start_sec = self._offset
        end_sec = start_sec + width_px / max(self._zoom * self._sr, 1e-6)
        bar_w = 2  # pixels
        n_bars = min(width_px // bar_w, 1_000, len(self._y) // 64)

        if n_bars == 0:
            self.scene().clear()
            return

        bars = self.project.wave_cache.bars(start_sec, end_sec, n_bars)
        if not bars:
            self.scene().clear()
            return

        # Build single path per bar
        mid_y = self.height() / 2
        scale_y = mid_y * 0.9
        base_colour = QColor(self.palette["waveform"])

        self.scene().clear()
        for i, (mn, mx, intensity) in enumerate(bars):
            x = i * bar_w
            y1 = mid_y + mn * scale_y
            y2 = mid_y + mx * scale_y

            colour = QColor(base_colour)
            colour.setAlphaF(max(0.3, intensity))
            pen = QPen(colour, bar_w)
            self.scene().addLine(x, y1, x, y2, pen)  # single vertical bar

    # ---------- viewport mechanics ----------
    def resizeEvent(self, _) -> None:
        super().resizeEvent(_)
        self._redraw_timer.start()

    # ---------- mouse interaction ----------
    def mousePressEvent(self, event) -> None:
        self._drag_origin = event.position()
        self._drag_active = False

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.LeftButton and self._drag_origin is not None:
            dist = (event.position() - self._drag_origin).manhattanLength()
            if dist > self._drag_threshold:
                self._drag_active = True

            dx = event.position().x() - self._drag_origin.x()
            sec_delta = dx / max(self._zoom * self._sr, 1e-6)
            max_offset = max(self._duration - self.width() / max(self._zoom * self._sr, 1e-6), 0.0)
            self._offset = max(0.0, min(self._offset - sec_delta, max_offset))

            self._redraw()
            self.viewport_changed.emit()
            self._drag_origin = event.position()  # continue drag

    def mouseReleaseEvent(self, event) -> None:
        if not self._drag_active:
            # Single click → seek
            sec = self._offset + event.position().x() / max(self._zoom * self._sr, 1e-6)
            self.seek_requested.emit(sec)
            self.stop_origin_changed.emit(sec)
        self._drag_active = False
        self._drag_origin = None

    # ---------- wheel zoom ----------
    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 1.0 / 1.1

        mouse_sec = self._offset + event.position().x() / max(self._zoom * self._sr, 1e-6)

        if event.modifiers() & Qt.ShiftModifier:
            # Horizontal scroll
            dx = -delta * 0.5 / max(self._zoom * self._sr, 1e-6)
            new_offset = self._offset + dx
        else:
            # Zoom around mouse
            self._zoom *= factor
            min_zoom = self.width() / (self._duration * self._sr + 1e-6)
            self._zoom = max(self._zoom, min_zoom)
            new_offset = mouse_sec - event.position().x() / (self._zoom * self._sr)

        max_offset = max(self._duration - self.width() / max(self._zoom * self._sr, 1e-6), 0.0)
        self._offset = max(0.0, min(new_offset, max_offset))

        self._redraw_timer.start()