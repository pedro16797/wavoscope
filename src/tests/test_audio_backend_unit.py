import pytest
import numpy as np
import sys
from unittest.mock import MagicMock, patch

# Mock sounddevice before importing AudioBackend if possible,
# or just rely on AudioBackend's internal guard.
# To patch 'sounddevice.OutputStream' when sounddevice doesn't exist:
mock_sd = MagicMock()
sys.modules["sounddevice"] = mock_sd

from audio.audio_backend import AudioBackend

@pytest.fixture
def mock_audio():
    with patch("soundfile.read") as mock_read:
        # Mock 1 second of silence at 44100Hz
        sr = 44100
        data = np.zeros(sr, dtype=np.float32)
        mock_read.return_value = (data, sr)

        backend = AudioBackend()
        backend.open_file("dummy.wav")
        return backend

def test_backend_initial_state(mock_audio):
    backend = mock_audio
    assert backend._sr == 44100
    assert backend.duration == 1.0
    assert backend.position == 0.0
    assert backend._playing is False

def test_seek_and_cursor(mock_audio):
    backend = mock_audio
    backend.seek(0.5)
    assert backend.position == 0.5
    assert backend._read_sample_idx == 22050

def test_speed_affects_stretcher(mock_audio):
    backend = mock_audio
    backend.set_speed(0.5)
    assert backend._speed == 0.5

def test_filter_constraints(mock_audio):
    backend = mock_audio
    # Set low > high
    backend.set_filter(low=1000, high=500)
    assert backend._filter_low_hz == 450.0
    assert backend._filter_high_hz == 500.0

def test_callback_cursor_update(mock_audio):
    backend = mock_audio
    backend.play()

    # Simulate callback
    outdata = np.zeros((512, 1), dtype=np.float32)
    backend._audio_callback(outdata, 512, None, None)

    # Cursor should advance: frames / sr * speed
    assert backend.position > 0
    assert backend.position == pytest.approx(512 / 44100)
