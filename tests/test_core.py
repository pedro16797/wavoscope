import sys
from unittest.mock import MagicMock

# Mock sounddevice and soundfile before they are imported by wavoscope
sys.modules['sounddevice'] = MagicMock()
sys.modules['soundfile'] = MagicMock()

import pytest
from pathlib import Path
import numpy as np
from wavoscope.audio.audio_backend import AudioBackend
from wavoscope.session.project import Project

def test_audio_backend_initialization():
    backend = AudioBackend()
    assert backend._playing is False
    assert backend._cursor == 0.0

def test_audio_backend_callbacks():
    backend = AudioBackend()
    called = False
    def callback():
        nonlocal called
        called = True

    backend.on_finished(callback)
    backend._on_finished()
    assert called is True

def test_project_initialization(tmp_path):
    audio_file = tmp_path / "test.wav"
    audio_file.touch()
    project = Project(audio_file)
    assert project.audio_path == audio_file
    assert project._flag_added_callbacks == []

def test_project_callbacks(tmp_path):
    audio_file = tmp_path / "test.wav"
    audio_file.touch()
    project = Project(audio_file)

    added_time = None
    def flag_added(t):
        nonlocal added_time
        added_time = t

    project.on_flag_added(flag_added)

    # Mocking dependencies to avoid real file loading/audio backend issues
    project.session_data = {"flags": []}

    # Need to mock backend.clear_tick_cache which is called by add_flag
    project.backend.clear_tick_cache = MagicMock()

    project.add_flag(1.5)

    assert added_time == 1.5
