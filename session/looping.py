from __future__ import annotations
import bisect
from typing import List, Dict, Any, Tuple

class LoopingEngine:
    def __init__(self):
        self.loop_mode: str = "none"

    def set_loop_mode(self, mode: str):
        self.loop_mode = mode

    def get_loop_range(self, pos: float, duration: float, flags: List[Dict[str, Any]], lyrics: List[Dict[str, Any]] = []) -> Tuple[float, float]:
        if self.loop_mode == "none" or self.loop_mode == "whole":
            return (0.0, duration)

        if self.loop_mode == "lyric" and lyrics:
            # Find the lyric that contains pos
            for l in lyrics:
                if l["timestamp"] <= pos <= l["timestamp"] + l["duration"]:
                    return (l["timestamp"], l["timestamp"] + l["duration"])
            # If not in a lyric, fall back to "bar" or "section"?
            # User says "loop the duration of the lyrics element",
            # so if we are outside we probably just use the closest or nothing.
            # Let's use the closest one or bar loop.
            return (0.0, duration)

        if self.loop_mode == "section":
            section_starts = [f["t"] for f in flags if f.get("is_section_start")]
            if not section_starts:
                return (0.0, duration)
            idx = bisect.bisect_right(section_starts, pos) - 1
            start = section_starts[idx] if idx >= 0 else 0.0
            end = section_starts[idx + 1] if idx + 1 < len(section_starts) else duration
            return (start, end)

        if self.loop_mode == "bar":
            times = [f["t"] for f in flags if f.get("type") == "rhythm"]
            if not times:
                return (0.0, duration)
            idx = bisect.bisect_right(times, pos) - 1
            start = times[idx] if idx >= 0 else 0.0
            end = times[idx + 1] if idx + 1 < len(times) else duration
            return (start, end)

        return (0.0, duration)
