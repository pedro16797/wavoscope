from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QColor
from wavoscope.gui.colours import load_palette

class FlagOverlay:
    """Lightweight helper for Timeline & Waveform to paint flags."""
    HEIGHT = 12          # px

    @staticmethod
    def paint(painter: QPainter, flags, start_sec, end_sec, width, height):
        if not flags or start_sec == end_sec:
            return
            
        palette = load_palette()
        colors = {
            "harmony": QColor(palette.get("flagHarmony", "#0f0")),
            "rhythm": QColor(palette.get("flagRhythm", "#f00")),
        }
        
        scale = width / (end_sec - start_sec)
        for flag in flags:
            x = int((flag["t"] - start_sec) * scale)
            rect = QRectF(x, 0, 3, FlagOverlay.HEIGHT)
            color = colors[flag["type"]]
            painter.fillRect(rect, color)