from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtGui import QBrush, QColor
from wavoscope.gui.timeline import Timeline
from wavoscope.gui.flag_context_menu import FlagContextMenu

class FlagItem(QGraphicsRectItem):
    WIDTH = 8
    HEIGHT = 12

    def __init__(self, flag_idx, time, parent=None):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT, parent)
        self.setBrush(QBrush(QColor("#f00")))
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.SizeHorCursor)
        self.setAcceptHoverEvents(True)
        self.flag_idx = flag_idx
        self._time = time

    def contextMenuEvent(self, event):
        views = self.scene().views()
        if not views:
            return
        main = views[0].window()
        if main and hasattr(main, 'project') and main.project:
            FlagContextMenu.show(
                views[0], main.project, self.flag_idx, event.screenPos()
            )
        event.accept()

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionChange:
            # Find the main window through the scene
            if self.scene() is None:
                return value
                
            views = self.scene().views()
            if not views:
                return value
                
            # Get the timeline and project
            timeline = views[0]
            main = timeline.window()
            if not main or not hasattr(main, 'project') or not main.project:
                return value
                
            # Get scale from waveform
            waveform = main.waveform
            view_start = waveform._offset
            scale = waveform.width() / max((waveform._zoom * waveform._sr), 1e-3)
            
            new_x = value.x()
            new_time = view_start + (new_x + self.WIDTH/2) / scale
            
            # Enforce boundaries
            flags = main.project.flags
            idx = self.flag_idx
            prev_t = flags[idx-1]["t"] if idx > 0 else 0
            next_t = flags[idx+1]["t"] if idx < len(flags)-1 else waveform._duration
            new_time = max(prev_t + 0.001, min(next_t - 0.001, new_time))
            
            # Snap to grid
            new_time = Timeline._snap_time(new_time)
            new_x = (new_time - view_start) * scale - self.WIDTH/2
            return new_x
        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        
        # Update project on release
        timeline = None
        for view in self.scene().views():
            if hasattr(view, 'window'):
                timeline = view
                break
                
        if timeline and timeline.window() and hasattr(timeline.window(), 'project'):
            main = timeline.window()
            waveform = main.waveform
            view_start = waveform._offset
            scale = waveform.width() / max((waveform._zoom * waveform._sr), 1e-3)
            
            new_time = view_start + (self.x() + self.WIDTH/2) / scale
            new_time = Timeline._snap_time(new_time)
            main.project.move_flag(self.flag_idx, new_time)