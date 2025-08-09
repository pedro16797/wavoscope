"""
Light-weight helper painting rhythm/harmony flags into Timeline & Waveform.
"""
from __future__ import annotations

from typing import List, Dict, Any

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QColor
from wavoscope.gui.colours import load_palette, current_theme


class FlagOverlay:
    """Static painter for small rectangular flag indicators."""

    HEIGHT: int = 12  # px

    @staticmethod
    def paint(
        painter: QPainter,
        flags: List[Dict[str, Any]],
        start_sec: float,
        end_sec: float,
        width: int,
        y_offset: int,
    ) -> None:
        """Draw flags along the horizontal timeline."""
        if not flags or start_sec == end_sec:
            return

        palette = load_palette(current_theme())
        colors = {
            "harmony": QColor(palette.get("flagHarmony", "#0f0")),
            "rhythm": QColor(palette.get("flagRhythm", "#f00")),
        }

        scale = width / (end_sec - start_sec)
        for flag in flags:
            x = int((flag["t"] - start_sec) * scale)
            w = 3
            color = colors[flag["type"]]
            if flag.get("is_section_start", False):
                color = color.lighter(150)
            rect = QRectF(x, y_offset, w, FlagOverlay.HEIGHT)
            painter.fillRect(rect, color)