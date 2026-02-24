import pytest
from pathlib import Path
from session.project import Project
from backend import state

def test_undo_manager_basic(tmp_path):
    audio_path = tmp_path / "test.wav"
    audio_path.write_bytes(b"dummy")

    project = Project(audio_path)

    # Step 0: Initial State
    history = project._undo.get_history()
    assert len(history) == 1
    assert history[0]["label"] == "Initial State"

    # Step 1: Add flag
    project.add_flag(1.0, kind="rhythm")
    history = project._undo.get_history()
    assert len(history) == 2
    assert "Added Rhythm Flag" in history[1]["label"]
    assert len(project.flags) == 1

    # Step 2: Add another flag
    project.add_flag(2.0, kind="rhythm")
    assert len(project.flags) == 2

    # Undo to Step 1
    project.restore_checkpoint(1)
    assert len(project.flags) == 1
    assert project.flags[0]["t"] == 1.0

    # History should be truncated
    history = project._undo.get_history()
    assert len(history) == 2

    # Undo to Step 0
    project.restore_checkpoint(0)
    assert len(project.flags) == 0
    history = project._undo.get_history()
    assert len(history) == 1

def test_undo_max_steps(tmp_path):
    audio_path = tmp_path / "test2.wav"
    audio_path.write_bytes(b"dummy")
    project = Project(audio_path)

    project._undo.set_max_steps(3)

    project.add_flag(1.0) # Step 1
    project.add_flag(2.0) # Step 2
    project.add_flag(3.0) # Step 3

    history = project._undo.get_history()
    assert len(history) == 4 # Initial + 3

    project.add_flag(4.0) # Truncates Initial State
    history = project._undo.get_history()
    assert len(history) == 4 # Base (was Step 1) + 3 steps
    assert "Added Rhythm Flag at 1.000s" in history[0]["label"]

    # Check that we can still restore to the new base
    project.restore_checkpoint(0)
    assert len(project.flags) == 1
    assert project.flags[0]["t"] == 1.0
