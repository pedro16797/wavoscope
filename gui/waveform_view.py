import numpy as np
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from wavoscope.gui.colours import load_palette

class WaveformView(QGraphicsView):
    # ---------- public helpers ----------
    def time_to_pixel(self, t):
        return (t - self._offset) * self._zoom * self._sr

    def pixel_to_time(self, x):
        return max(0, min(self._offset + x / (self._zoom * self._sr), self._audio_duration))
    
    @property
    def _duration(self):
        return self.project.duration if self.project else 0.0

    seek_requested = Signal(float)
    viewport_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)

        self.project = None
        self._y = None
        self._sr = 44100
        self._audio_duration = 0
        self._offset = 0.0
        self._zoom = 1.0
        self._cursor = 0.0
        self._drag_threshold = 10  # px
        self._drag_active = False
        self._drag_origin = 0

        self._redraw_timer = QTimer(self)
        self._redraw_timer.setSingleShot(True)
        self._redraw_timer.setInterval(50)
        self._redraw_timer.timeout.connect(self._redraw)
        self._frame_count = 0

    # ---------- public ----------
    def setProject(self, project):
        self.project = project
        self.set_audio_data(project._data, project._sr)

    def set_audio_data(self, y, sr):
        self._y = y.astype(np.float32)
        self._sr = sr
        self._audio_duration = len(y) / sr
        self.set_viewport_range(0, self._audio_duration)

    def set_viewport_range(self, start_sec, end_sec):
        self._offset = start_sec
        self._zoom = self.width() / max((end_sec - start_sec) * self._sr, 1)
        self._redraw()
        self.viewport_changed.emit()

    def set_cursor(self, sec):
        self._cursor = sec
        self.viewport().update()

    # ---------- drawing ----------
    def _on_theme_changed(self, name):
        self.palette = load_palette(name)
        self._redraw()

    def _redraw(self):
        if (self.project is None or
            self.project.wave_cache is None or
            self.width() <= 0 or
            self._zoom <= 0):
            return

        w = self.width()
        start_sec = self._offset
        end_sec = start_sec + w / max(self._zoom * self.project.wave_cache.sr, 1)
        bar_w = 2
        n_bars = min(w // bar_w, 1000,
                     len(self.project.wave_cache.y) // 64)

        if n_bars == 0:
            self.scene().clear()
            return

        bars = self.project.wave_cache.bars(start_sec, end_sec, n_bars)
        if not bars:
            self.scene().clear()
            return

        # Build one path per bar with its own colour
        mid = self.height() / 2
        scale = mid * 0.9
        base_colour = QColor(self.palette["waveform"])
        
        self.scene().clear()

        for i, (mn, mx, intensity) in enumerate(bars):
            x = i * bar_w
            y1 = mid + mn * scale
            y2 = mid + mx * scale

            colour = QColor(base_colour)
            colour.setAlphaF(max(0.3, intensity))   # darker when intensity < 1
            pen = QPen(colour, bar_w)

            self.scene().addLine(x, y1, x, y2, pen)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._redraw_timer.start()

    def mousePressEvent(self, event):
        self._drag_origin = event.position()
        self._drag_active = False

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            dist = (event.position() - self._drag_origin).manhattanLength()
            if dist > self._drag_threshold:
                self._drag_active = True
            dx = event.position().x() - self._drag_origin.x()
            secs = dx / max(self._zoom * self._sr, 1)
            max_offset = self._audio_duration - self.width() / max(self._zoom * self._sr, 1e-3)
            self._offset = max(0, min(self._offset - secs, max_offset))
            self._redraw()
            self.viewport_changed.emit()

    def mouseReleaseEvent(self, event):
        if not self._drag_active:
            sec = self._offset + event.position().x() / max(self._zoom * self._sr, 1)
            self.seek_requested.emit(sec)
        self._drag_active = False

    # ---------- wheel ----------
    def wheelEvent(self, e: QWheelEvent):
        delta = e.angleDelta().y()
        factor = 1.1 if delta > 0 else 1 / 1.1
        mouse_sec = self._offset + e.position().x() / max(self._zoom * self.project.wave_cache.sr, 1e-3)

        if e.modifiers() & Qt.ShiftModifier:
            dx = -delta * 0.5 / max(self._zoom * self.project.wave_cache.sr, 1e-3)
            new_offset = self._offset + dx
        else:
            self._zoom *= factor
            min_zoom = self.width() / (self._audio_duration * self.project.wave_cache.sr + 1e-6)
            self._zoom = max(self._zoom, min_zoom)
            new_offset = mouse_sec - e.position().x() / (self._zoom * self.project.wave_cache.sr)

        # --- clamp ---
        max_offset = max(self._audio_duration - self.width() / max(self._zoom * self.project.wave_cache.sr, 1e-3), 0)
        self._offset = max(0, min(new_offset, max_offset))

        self._redraw_timer.start()