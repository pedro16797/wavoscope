import sys
from pathlib import Path
from unittest.mock import MagicMock
import types

# Robust way to ensure 'wavoscope' is importable regardless of structure
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

if "wavoscope" not in sys.modules:
    wavoscope = types.ModuleType("wavoscope")
    wavoscope.__path__ = [str(root)]
    sys.modules["wavoscope"] = wavoscope

# Mock sounddevice and soundfile before they are imported by wavoscope
sys.modules['sounddevice'] = MagicMock()
sys.modules['soundfile'] = MagicMock()

import pytest
import numpy as np
from wavoscope.audio.audio_backend import AudioBackend
from wavoscope.session.project import Project
from wavoscope.audio.waveform_cache import WaveformCache
from wavoscope.audio.ringbuffer import RingBuffer

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
    assert project._flags_updated_callbacks == []

def test_project_callbacks(tmp_path):
    audio_file = tmp_path / "test.wav"
    audio_file.touch()
    project = Project(audio_file)

    updated = False
    def flags_updated():
        nonlocal updated
        updated = True

    project.on_flags_updated(flags_updated)

    # Mocking dependencies to avoid real file loading/audio backend issues
    project.session_data = {"flags": []}

    # Need to mock backend.clear_tick_cache which is called by add_flag
    project.backend.clear_tick_cache = MagicMock()

    project.add_flag(1.5)

    assert updated is True

def test_waveform_cache():
    sr = 1000
    y = np.sin(2 * np.pi * 5 * np.linspace(0, 1, sr)) # 1 second of 5Hz sine
    cache = WaveformCache(y, sr)

    # 10 bars for the whole duration
    bars = cache.bars(0.0, 1.0, 10)
    assert len(bars) == 10
    for min_val, max_val, intensity in bars:
        assert -1.1 <= min_val <= 1.1
        assert -1.1 <= max_val <= 1.1
        assert 0.0 <= intensity <= 1.0

def test_ring_buffer():
    rb = RingBuffer(100)
    data = np.ones(50, dtype=np.float32)
    rb.write(data)

    read_data = rb.read(50)
    assert np.all(read_data == 1.0)

    # Test underrun (should return zeros)
    read_empty = rb.read(10)
    assert np.all(read_empty == 0.0)

    # Test wrap around
    rb.write(np.ones(80, dtype=np.float32)) # 80 + 50 used = 130 > 100, but read 50 so 30 used. 30 + 80 = 110.
    # Write 80 into 100-size buffer where 0 is start (read_idx was 50, now 50+50=100 so 0).
    # write_idx was 50, writing 80 makes it (50+80)%100 = 30.
    # buffer has ones from 50 to 100 and 0 to 30.
    # Wait, write_idx was 50. Writing 80.
    # buf[50:100] = ones[:50]
    # buf[0:30] = ones[50:80]
    # read_idx is 50.
    # read(100) should return 100 ones.
    read_full = rb.read(80)
    assert np.all(read_full == 1.0)
