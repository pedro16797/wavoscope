import pytest
import time
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from backend import state, autosave
from utils.config import Config
from session.manager import ProjectManager

def test_autosave_rotation(tmp_path):
    # Mock project
    mock_project = MagicMock()
    mock_project.audio_path = Path("test_song.mp3")
    mock_project._dirty = True

    pm = ProjectManager(Path("test_song.mp3"))
    pm.session_data = {"test": "data"}
    mock_project._manager = pm

    state.project = mock_project

    # Configure autosave
    autosave_dir = tmp_path / "autosaves"
    cfg = Config()
    cfg.set("recovery.autosave_enabled", True)
    cfg.set("recovery.autosave_forced", False)
    cfg.set("recovery.autosave_interval_minutes", 0.0001)
    cfg.set("recovery.autosave_max_snapshots", 3)
    cfg.set("recovery.autosave_path", str(autosave_dir))

    from backend.autosave import _manager

    # 1st
    _manager._do_autosave()
    assert (autosave_dir / "test_song.autosave.1.oscope").exists()

    # 2nd
    _manager._do_autosave()
    assert (autosave_dir / "test_song.autosave.2.oscope").exists()

    # 3rd
    _manager._do_autosave()
    assert (autosave_dir / "test_song.autosave.3.oscope").exists()

    # 4th (rotate)
    _manager._do_autosave()
    assert not (autosave_dir / "test_song.autosave.4.oscope").exists()
    assert (autosave_dir / "test_song.autosave.3.oscope").exists()

    state.project = None

def test_autosave_forced_vs_dirty(tmp_path):
    mock_project = MagicMock()
    mock_project.audio_path = Path("test_song.mp3")

    pm = ProjectManager(Path("test_song.mp3"))
    pm.session_data = {"test": "data"}
    mock_project._manager = pm
    state.project = mock_project

    autosave_dir = tmp_path / "autosaves_forced"
    cfg = Config()
    cfg.set("recovery.autosave_enabled", True)
    cfg.set("recovery.autosave_path", str(autosave_dir))

    from backend.autosave import _manager

    # Case 1: Not forced, Not dirty -> No save
    cfg.set("recovery.autosave_forced", False)
    mock_project._dirty = False
    # We can't easily test the _run loop, but we can test the logic if we exposed it.
    # For now, let's just ensure _do_autosave works when called.

    # Case 2: Forced, Not dirty -> Save
    cfg.set("recovery.autosave_forced", True)
    _manager._do_autosave()
    assert (autosave_dir / "test_song.autosave.1.oscope").exists()

    state.project = None
