"""
Horizontal timeline ruler with time-grid, flags, and subdivision bars.
Supports drag-to-reorder and right-click menu for flags.
"""
from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, QElapsedTimer, QPoint, Signal
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget

from wavoscope.gui.colours import load_palette
from wavoscope.gui.flag_overlay import FlagOverlay
from wavoscope.gui.flag_context_menu import FlagContextMenu

SNAP_GRID_S = 0.01  # 10 ms grid


class Timeline(QWidget):
    """Time ruler that displays flags and subdivision ticks."""

    seek_requested = Signal(float)
    flag_mode_changed = Signal(object)  # FlagMode enum

    @staticmethod
    def _snap_time(t: float) -> float:
        """Quantise time to 50 ms grid."""
        return round(t / SNAP_GRID_S) * SNAP_GRID_S

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(42)
        self._latency_timer = QElapsedTimer()

        # Audio state
        self._duration: float = 0.0
        self._cursor: float = 0.0
        self._sr: int = 44_100

        # Drag state
        self._drag_idx: int | None = None
        self._drag_start_x: float = 0.0
        self._drag_start_t: float = 0.0

    # ---------- public ----------
    def set_audio_data(self, y: np.ndarray, sr: int) -> None:
        """Called when new audio is loaded."""
        self._duration = len(y) / sr
        self._sr = sr
        self.update()

    def set_cursor(self, sec: float) -> None:
        """Move play-head line."""
        self._cursor = sec
        self.update()

    def _on_theme_changed(self, name: str) -> None:
        """React to palette change."""
        self.palette = load_palette(name)
        self.update()

    def _on_mode_clicked(self) -> None:
        """Placeholder for future harmony mode toggle."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Harmony flags", "Harmony mode – coming soon!")

    # ---------- painting ----------
    def paintEvent(self, _) -> None:
        if not self._duration or self.width() <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fetch shared viewport parameters
        main = self.window()
        if not (main and hasattr(main, "waveform")):
            return
        waveform = main.waveform
        view_start = waveform._offset
        view_span = self.width() / max(waveform._zoom * waveform._sr, 1e-3)
        view_end = view_start + view_span

        # Time-grid & labels
        step = max(1, int(view_span / 15))  # Aim for ~15 labels
        for sec in range(int(view_start), int(view_end) + 1, step):
            x = int((sec - view_start) * self.width() / view_span)
            m, s = divmod(sec, 60)
            painter.setPen(QColor(self.palette["grid"]))
            painter.drawText(x + 2, 14, f"{m}:{s:02d}")
            painter.drawLine(x, 0, x, self.height())

        # Play-head
        x = int((self._cursor - view_start) * self.width() / view_span)
        painter.setPen(QPen(QColor(self.palette["accent"]), 2))
        painter.drawLine(x, 0, x, self.height())

        # Flags
        if hasattr(main, "project") and main.project:
            flags = main.project.flags
            FlagOverlay.paint(painter, flags, view_start, view_end, self.width(), 12)

            # Flag names
            painter.setPen(QColor(self.palette["text"]))
            font = painter.font()
            font.setPixelSize(9)
            font.setFamily("Consolas")
            painter.setFont(font)
            for f in flags:
                if f["type"] != "rhythm":
                    continue
                x = int((f["t"] - view_start) * self.width() / view_span)
                name = name = f.get("name") or f.get("auto_name", "")
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

            # Subdivision ticks
            for prev, nxt in zip(flags, flags[1:]):
                if prev["type"] != "rhythm":
                    continue
                subdiv = prev.get("subdivision", 0)
                if subdiv == 0:
                    # Walk backwards for first non-zero subdivision
                    for p in reversed(flags[: flags.index(prev) + 1]):
                        if p["type"] == "rhythm" and p.get("subdivision", 0) != 0:
                            subdiv = p["subdivision"]
                            break
                    else:
                        subdiv = 1

                if subdiv <= 1:
                    continue

                span = nxt["t"] - prev["t"]
                step = span / subdiv
                shaded = prev.get("shaded_subdivisions", False)

                for k in range(1, subdiv):
                    x = int((prev["t"] + k * step - view_start) * self.width() / view_span)
                    if shaded and k % 2 == 1:
                        painter.setPen(QPen(QColor(self.palette["accent"]).lighter(150), 1, Qt.DotLine))
                        painter.drawLine(x, 15, x, self.height() - 5)
                    else:
                        painter.setPen(QPen(QColor(self.palette["accent"]).lighter(120), 1, Qt.DotLine))
                        painter.drawLine(x, 10, x, self.height())
        if getattr(main, "_debug_latency", False):
            painter.setPen(QColor("#ffff00"))
            font = painter.font()
            font.setPixelSize(11)
            painter.setFont(font)
            painter.drawText(4, 14, self._latency_text())

    # ---------- mouse interaction ----------
    def mousePressEvent(self, event) -> None:
        """Left-click = add / drag flag; Right-click = context menu."""
        if event.button() == Qt.RightButton:
            self._open_context_menu(event.globalPosition().toPoint())
            return

        if event.button() != Qt.LeftButton:
            return

        main = self.window()
        if not (main and hasattr(main, "project") and main.project):
            return

        waveform = main.waveform
        view_start = waveform._offset
        view_span = self.width() / max(waveform._zoom * waveform._sr, 1e-3)
        click_t = view_start + event.position().x() * view_span / self.width()

        # Look for closest flag within 10 px
        scale = self.width() / view_span
        min_dist = 10.0 / scale
        best_idx = None
        for idx, f in enumerate(main.project.flags):
            if f["type"] != "rhythm":
                continue
            if abs(f["t"] - click_t) < min_dist:
                best_idx = idx
                min_dist = abs(f["t"] - click_t)

        if best_idx is not None:
            self._drag_idx = best_idx
            self._drag_start_x = event.position().x()
            self._drag_start_t = main.project.flags[best_idx]["t"]
            return

        # No nearby flag → add new
        snapped_t = self._snap_time(click_t)
        main.project.add_flag(snapped_t, "rhythm")
        self.update()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_idx is None:
            return

        main = self.window()
        if not (main and hasattr(main, "project") and main.project):
            return

        waveform = main.waveform
        dx = event.position().x() - self._drag_start_x
        dt = dx / max(waveform._zoom * waveform._sr, 1e-3)
        new_t = self._snap_time(self._drag_start_t + dt)

        # Clamp between neighbours
        flags = main.project.flags
        prev_t = flags[self._drag_idx - 1]["t"] if self._drag_idx > 0 else 0
        next_t = flags[self._drag_idx + 1]["t"] if self._drag_idx < len(flags) - 1 else self._duration
        new_t = max(prev_t + 0.001, min(next_t - 0.001, new_t))
        main.project.move_flag(self._drag_idx, new_t)
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if self._drag_idx is not None:
            self._drag_idx = None
        else:
            super().mouseReleaseEvent(event)

    # ---------- helpers ----------
    def _open_context_menu(self, global_pos: QPoint) -> None:
        """Open right-click context menu for nearest flag."""
        main = self.window()
        if not (main and hasattr(main, "project") and main.project):
            return

        waveform = main.waveform
        view_start = waveform._offset
        view_span = self.width() / max(waveform._zoom * waveform._sr, 1e-3)
        click_t = view_start + self.mapFromGlobal(global_pos).x() * view_span / self.width()

        min_dist = 10.0 / (self.width() / view_span)
        best_idx = None
        for idx, f in enumerate(main.project.flags):
            if abs(f["t"] - click_t) < min_dist:
                best_idx = idx
                min_dist = abs(f["t"] - click_t)

        if best_idx is not None:
            FlagContextMenu.show(
                self, main.project, best_idx, global_pos, self._snap_time
            )
    
    def _latency_text(self) -> str:
        """Return Δ (visual − audio) in ms, or empty string."""
        main = self.window()
        if not (main and main.project):
            return ""
        audio_t = main.project.position
        visual_t = self._cursor
        delta_ms = (visual_t - audio_t) * 1000.0
        return f"{delta_ms:+.1f} ms"