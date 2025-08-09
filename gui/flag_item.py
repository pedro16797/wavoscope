"""
Draggable graphics item representing a single flag on the Timeline.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem

from wavoscope.gui.flag_context_menu import FlagContextMenu

if TYPE_CHECKING:
    from wavoscope.gui.timeline import Timeline


class FlagItem(QGraphicsRectItem):
    """Red (rhythm) or green (harmony) vertical bar that the user can drag."""

    WIDTH: int = 8
    HEIGHT: int = 12

    def __init__(self, flag_idx: int, time: float, parent=None) -> None:
        super().__init__(0, 0, self.WIDTH, self.HEIGHT, parent)
        self.setBrush(QBrush(QColor("#f00")))  # Default red
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.SizeHorCursor)
        self.setAcceptHoverEvents(True)

        self.flag_idx: int = flag_idx
        self._time: float = time  # cached logical time

    # ---------- context menu ----------
    def contextMenuEvent(self, event) -> None:
        views = self.scene().views()
        if not views:
            return

        main_win = views[0].window()
        if main_win and hasattr(main_win, "project") and main_win.project:
            FlagContextMenu.show(
                views[0], main_win.project, self.flag_idx, event.screenPos()
            )
        event.accept()

    # ---------- dragging with snapping ----------
    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionChange and self.scene():
            views = self.scene().views()
            if not views:
                return value

            timeline = views[0]  # Timeline view
            main = timeline.window()
            if not (main and hasattr(main, "project") and main.project):
                return value

            waveform = main.waveform
            view_start = waveform._offset
            scale = waveform.width() / max(
                waveform._zoom * waveform._sr, 1e-3
            )

            new_x = value.x()
            new_time = view_start + (new_x + self.WIDTH / 2) / scale

            # Boundaries between neighbouring flags
            flags = main.project.flags
            prev_t = flags[self.flag_idx - 1]["t"] if self.flag_idx > 0 else 0
            next_t = (
                flags[self.flag_idx + 1]["t"]
                if self.flag_idx < len(flags) - 1
                else waveform._duration
            )
            new_time = max(prev_t + 0.001, min(next_t - 0.001, new_time))
            new_time = Timeline._snap_time(new_time)
            new_x = (new_time - view_start) * scale - self.WIDTH / 2
            return new_x
        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)

        # Commit new position to project
        for view in self.scene().views():
            if hasattr(view, "window"):
                main = view.window()
                if main and hasattr(main, "project"):
                    waveform = main.waveform
                    view_start = waveform._offset
                    scale = waveform.width() / max(
                        waveform._zoom * waveform._sr, 1e-3
                    )
                    new_time = view_start + (self.x() + self.WIDTH / 2) / scale
                    new_time = Timeline._snap_time(new_time)
                    main.project.move_flag(self.flag_idx, new_time)
                break