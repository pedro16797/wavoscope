import pytest
from pathlib import Path
from session.project import Project
from unittest.mock import MagicMock

@pytest.fixture
def dummy_project(tmp_path):
    # Mock AudioBackend to avoid starting real streams
    with MagicMock() as mock_backend:
        mock_backend.duration = 100.0
        mock_backend.position = 0.0
        mock_backend._sr = 44100
        mock_backend._playing = False

        # We need to ensure Project uses our mock
        import session.project
        original_backend = session.project.AudioBackend
        session.project.AudioBackend = MagicMock(return_value=mock_backend)

        audio_path = tmp_path / "test.wav"
        audio_path.write_bytes(b"") # Empty dummy

        proj = Project(audio_path)

        # Restore
        session.project.AudioBackend = original_backend
        return proj, mock_backend

def test_subdivision_ticks(dummy_project):
    proj, _ = dummy_project

    # Add rhythm flags
    proj.add_flag(0.0, type="rhythm", div=4)
    proj.add_flag(1.0, type="rhythm", div=4)
    proj.add_flag(2.0, type="rhythm", div=1)

    # Check ticks between 0.0 and 1.0 (exclusive end usually)
    # 0.0 (strong), 0.25, 0.5, 0.75 (weak)
    ticks = proj.subdivision_ticks_between(0.0, 0.99)
    assert len(ticks) == 4
    assert ticks[0] == (0.0, True)
    assert ticks[1] == (0.25, False)
    assert ticks[2] == (0.5, False)
    assert ticks[3] == (0.75, False)

def test_loop_range_logic(dummy_project):
    proj, mock_backend = dummy_project

    proj.add_flag(0.0, type="rhythm", s=True)
    proj.add_flag(10.0, type="rhythm", s=True)
    proj.add_flag(20.0, type="rhythm", s=False) # Just a rhythm flag

    # Mode: Whole
    proj.set_loop_mode("whole")
    assert proj.get_loop_range(5.0) == (0.0, 100.0)

    # Mode: Section
    proj.set_loop_mode("section")
    # At 5.0, should be between 0.0 and 10.0
    assert proj.get_loop_range(5.0) == (0.0, 10.0)
    # At 15.0, should be between 10.0 and 100.0 (no further sections)
    assert proj.get_loop_range(15.0) == (10.0, 100.0)

    # Mode: Bar
    proj.set_loop_mode("bar")
    # At 5.0, should be between 0.0 and 10.0
    assert proj.get_loop_range(5.0) == (0.0, 10.0)
    # At 15.0, should be between 10.0 and 20.0
    assert proj.get_loop_range(15.0) == (10.0, 20.0)

def test_loop_range_lyrics(dummy_project):
    proj, _ = dummy_project
    proj.add_lyric(s="Word1", t=1.0, l=2.0)
    proj.add_lyric(s="Word2", t=4.0, l=1.0)

    proj.set_loop_mode("lyric")

    # Selected lyric
    proj.set_selected_lyric(0)
    assert proj.get_loop_range(0.0) == (1.0, 3.0)

    proj.set_selected_lyric(1)
    assert proj.get_loop_range(0.0) == (4.0, 5.0)

    # No selection, should find lyric at position
    proj.set_selected_lyric(None)
    assert proj.get_loop_range(1.5) == (1.0, 3.0)
    assert proj.get_loop_range(4.2) == (4.0, 5.0)

def test_auto_naming(dummy_project):
    proj, _ = dummy_project
    proj.add_flag(0.0, type="rhythm", s=True)
    proj.add_flag(1.0, type="rhythm")
    proj.add_flag(2.0, type="rhythm", s=True)

    flags = proj.flags
    assert flags[0]["auto_name"] == "A"
    assert flags[1]["auto_name"] == "A01"
    assert flags[2]["auto_name"] == "B"
