from typing import Optional, Callable
from session.project import Project
from session.playlist import PlaylistManager

project: Optional[Project] = None
port: int = 8000

# Set during app startup; invoked from the audio backend when a track finishes.
on_playback_finished: Optional[Callable[[], None]] = None

playlist_manager = PlaylistManager()
active_playlist_id: Optional[str] = None
active_item_id: Optional[str] = None

# Export state
export_active: bool = False
export_progress: float = 0.0
export_message: str = ""
