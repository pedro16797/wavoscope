import threading
from typing import Optional, Callable
from session.project import Project
from session.playlist import PlaylistManager
from utils.logging import logger

project: Optional[Project] = None
port: int = 8000

# Serializes swapping the active project. Without it a route-driven open and an
# audio-thread playlist auto-advance can race and leak / double-close a project.
project_lock = threading.RLock()

# Set during app startup; invoked from the audio backend when a track finishes.
on_playback_finished: Optional[Callable[[], None]] = None


def set_project(new_project: Optional[Project]) -> None:
    """Atomically make `new_project` active and close the previous one.

    Callers create and open `new_project` first; the previous project is closed
    *after* the swap, so a reader never observes a closed-but-current project.
    """
    global project
    with project_lock:
        old = project
        project = new_project
    if old is not None and old is not new_project:
        try:
            old.close()
        except Exception:
            logger.exception("Error closing previous project")

playlist_manager = PlaylistManager()
active_playlist_id: Optional[str] = None
active_item_id: Optional[str] = None

# Export state
export_active: bool = False
export_progress: float = 0.0
export_message: str = ""
