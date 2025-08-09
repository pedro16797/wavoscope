from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from wavoscope.gui.colours import load_palette
from wavoscope.gui.waveform_view import WaveformView
from wavoscope.gui.flag_overlay import FlagOverlay
from wavoscope.gui.flag_context_menu import FlagContextMenu

from enum import Enum, auto
class FlagMode(Enum):
    RHYTHM = auto()
    HARMONY = auto()

SNAP_GRID_S = 0.05

class Timeline(QWidget):
    seek_requested = Signal(float)
    flag_mode_changed = Signal(FlagMode)
    SNAP_GRID_S = SNAP_GRID_S

    @staticmethod
    def _snap_time(t):
        return round(t / SNAP_GRID_S) * SNAP_GRID_S

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(42)
        self._duration = 0.0
        self._cursor = 0.0
        self._sr = 44100
        self._flag_mode = FlagMode.RHYTHM
        self._drag_idx = None
        self._drag_start_x = 0.0
        self._drag_start_t = 0.0
        self._last_update = 0

    def set_audio_data(self, y, sr):
        self._y = y
        self._sr = sr
        self._duration = len(y) / sr
        self.update()

    def set_cursor(self, sec):
        self._cursor = sec
        self.update()

    def _on_theme_changed(self, name):
        self.palette = load_palette(name)
        self.update()

    def _on_mode_clicked(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Harmony flags", "Harmony mode – coming soon!")

    def paintEvent(self, event):
        if not self._duration or self.width() <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        main = self.window()
        if not main or not hasattr(main, 'waveform'):
            return
            
        waveform = main.waveform
        view_start = waveform._offset
        view_end = view_start + self.width() / max(waveform._zoom * waveform._sr, 1e-3)
        span = max(view_end - view_start, 1e-3)

        # grid lines and time labels
        step = max(1, int(span / 15))
        for sec in range(int(view_start), int(view_end) + 1, step):
            x = int((sec - view_start) * self.width() / span)
            m, s = divmod(sec, 60)
            painter.setPen(QColor(self.palette["grid"]))
            painter.drawText(x + 2, 14, f"{m}:{s:02d}")
            painter.drawLine(x, 0, x, self.height())

        # cursor line
        x = int((self._cursor - view_start) * self.width() / span)
        painter.setPen(QPen(QColor(self.palette["accent"]), 2))
        painter.drawLine(x, 0, x, self.height())

        # flags
        if main and hasattr(main, 'project') and main.project:
            flags = main.project.flags
            FlagOverlay.paint(painter, flags,
                              view_start, view_end,
                              self.width(), 12)
            # draw flag names
            painter.setPen(QColor(self.palette["text"]))
            font = painter.font()
            font.setPixelSize(9)
            font.setFamily("Consolas")
            painter.setFont(font)
            for f in flags:
                if f["type"] != "rhythm":
                    continue
                x = int((f["t"] - view_start) * self.width() / span)
                name = f.get("name", "")
                fm = painter.fontMetrics()
                text_width = fm.horizontalAdvance(name)
                text_x = x - text_width // 2
                text_y = 11
                text_rect = fm.boundingRect(name)
                text_rect.moveTo(text_x, text_y - fm.ascent())
                text_rect.adjust(-2, -1, 2, 1)

                painter.fillRect(text_rect, QColor(self.palette["surface"]))
                painter.setPen(QColor(self.palette["text"]))
                painter.drawText(text_x, text_y, name)

            # subdivision bars with shading
            for prev, nxt in zip(flags, flags[1:]):
                if prev["type"] != "rhythm":
                    continue
                subdiv = prev.get("subdivision", 0)
                if subdiv == 0 or subdiv is None:
                    # walk backwards for the first rhythm flag with a non-zero value
                    for p in reversed(flags[:flags.index(prev)+1]):
                        if p["type"] == "rhythm" and p.get("subdivision", 0) != 0:
                            subdiv = p["subdivision"]
                            break
                    else:
                        subdiv = 1
                
                if subdiv <= 1:
                    continue
                
                step = (nxt["t"] - prev["t"]) / subdiv
                shaded = prev.get("shaded_subdivisions", False)
                
                for k in range(1, subdiv):
                    x = int((prev["t"] + k * step - view_start) * self.width() / span)
                    
                    if shaded and k % 2 == 1:  # 8th notes (odd positions)
                        # Shorter and lighter lines
                        painter.setPen(QPen(QColor(self.palette["accent"]).lighter(150), 1, Qt.DotLine))
                        painter.drawLine(x, 15, x, self.height() - 5)  # Shorter line
                    else:
                        # Normal subdivision lines
                        painter.setPen(QPen(QColor(self.palette["accent"]).lighter(120), 1, Qt.DotLine))
                        painter.drawLine(x, 10, x, self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            waveform = self.parent().findChild(WaveformView)
            if not waveform:
                return

            view_start = waveform._offset
            view_span = self.width() / max(waveform._zoom * waveform._sr, 1e-3)
            click_t = view_start + event.position().x() * view_span / self.width()

            best_idx = None
            min_dist = 10.0 / (self.width() / view_span)
            for idx, f in enumerate(self.window().project.flags):
                d = abs(f["t"] - click_t)
                if d < min_dist:
                    best_idx = idx
                    min_dist = d

            if best_idx is not None:
                FlagContextMenu.show(
                    self, self.window().project, best_idx,
                    event.globalPosition().toPoint(), Timeline._snap_time
                )
                event.accept()
                return

        if event.button() != Qt.LeftButton:
            super().mousePressEvent(event)
            return

        waveform = self.parent().findChild(WaveformView)
        if not waveform:
            return

        view_start = waveform._offset
        view_span  = self.width() / max(waveform._zoom * waveform._sr, 1e-3)
        click_t = view_start + event.position().x() * view_span / self.width()

        # Find closest flag within 10 px
        scale = self.width() / view_span
        best_idx = None
        min_dist = 10.0 / scale   # px → seconds
        for idx, f in enumerate(self.window().project.flags):
            if f["type"] != "rhythm":
                continue
            d = abs(f["t"] - click_t)
            if d < min_dist:
                best_idx = idx
                min_dist = d

        if best_idx is not None:
            self._drag_idx = best_idx
            self._drag_start_x = event.position().x()
            self._drag_start_t = self.window().project.flags[best_idx]["t"]
            event.accept()
            return

        snapped = self._snap_time(click_t)
        self.window().project.add_flag(snapped, "rhythm")
        self.update()

    def mouseMoveEvent(self, event):
        if self._drag_idx is None:
            return
        dx = event.position().x() - self._drag_start_x
        waveform = self.parent().findChild(WaveformView)
        zoom_factor = waveform._zoom * waveform._sr
        dt = dx / max(zoom_factor, 1e-3)
        new_t = self._drag_start_t + dt

        # clamp & snap
        new_t = max(0.0, min(new_t, self._duration))
        flags = self.window().project.flags
        prev_t = flags[self._drag_idx - 1]["t"] if self._drag_idx > 0 else 0
        next_t = flags[self._drag_idx + 1]["t"] if self._drag_idx < len(flags) - 1 else self._duration
        new_t = max(prev_t + 0.001, min(next_t - 0.001, new_t))
        new_t = self._snap_time(new_t)

        self.window().project.move_flag(self._drag_idx, new_t)
        self.update()

    def mouseReleaseEvent(self, event):
        if self._drag_idx is not None:
            self._drag_idx = None
        else:
            super().mouseReleaseEvent(event)