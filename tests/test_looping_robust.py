import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from audio.audio_backend import AudioBackend
from session.looping import LoopingEngine

def test_bar_loop_before_first_marker():
    engine = LoopingEngine()
    flags = [
        {"t": 10.0, "type": "rhythm", "div": 4},
        {"t": 20.0, "type": "rhythm", "div": 4}
    ]
    engine.set_loop_mode("bar")
    # If playhead is at 5.0, it should loop the first bar: 10.0 to 20.0
    # and playback should be allowed to reach 20.0 before jumping back to 10.0.
    lstart, lend = engine.get_loop_range(5.0, 100.0, flags)
    assert lstart == 10.0
    assert lend == 20.0

def test_whole_song_loop_eof():
    with patch("soundfile.read") as mock_read:
        sr = 44100
        # 1 second of audio
        data = np.zeros(sr, dtype=np.float32)
        mock_read.return_value = (data, sr)

        backend = AudioBackend()
        backend.open_file("dummy.wav")
        backend.set_loop_enabled(True)
        # Whole song mode
        backend.sync_project_data(flags=[], lyrics=[], loop_mode="whole", selected_lyric_idx=None, duration=1.0)

        backend.play()
        # Seek near end
        backend.seek(0.99)

        # Simulate callback that hits EOF
        outdata = np.zeros((1024, 1), dtype=np.float32)
        backend._audio_callback(outdata, 1024, None, None)

        # Should have looped back to 0.0 and still be playing
        assert backend.position < 0.1
        assert backend._playing is True

def test_last_bar_loop_eof():
    with patch("soundfile.read") as mock_read:
        sr = 44100
        data = np.zeros(sr, dtype=np.float32)
        mock_read.return_value = (data, sr)

        backend = AudioBackend()
        backend.open_file("dummy.wav")
        backend.set_loop_enabled(True)

        # Last bar: 0.5 to 1.0
        flags = [{"t": 0.5, "type": "rhythm", "div": 4}]
        backend.sync_project_data(flags=flags, lyrics=[], loop_mode="bar", selected_lyric_idx=None, duration=1.0)

        backend.play()
        backend.seek(0.99)

        outdata = np.zeros((1024, 1), dtype=np.float32)
        backend._audio_callback(outdata, 1024, None, None)

        # Should have looped back to 0.5
        assert 0.5 <= backend.position < 0.6
        assert backend._playing is True

def test_section_loop_before_first_marker():
    engine = LoopingEngine()
    flags = [
        {"t": 10.0, "type": "rhythm", "div": 4, "s": True},
        {"t": 30.0, "type": "rhythm", "div": 4, "s": True}
    ]
    engine.set_loop_mode("section")
    # If playhead is at 5.0, it should loop the first section: 10.0 to 30.0
    lstart, lend = engine.get_loop_range(5.0, 100.0, flags)
    assert lstart == 10.0
    assert lend == 30.0

def test_lyric_loop_before_first_marker():
    engine = LoopingEngine()
    lyrics = [
        {"t": 10.0, "l": 5.0, "s": "first"}
    ]
    engine.set_loop_mode("lyric")
    # If playhead is at 5.0, it should loop the first lyric: 10.0 to 15.0
    lstart, lend = engine.get_loop_range(5.0, 100.0, [], lyrics)
    assert lstart == 10.0
    assert lend == 15.0
