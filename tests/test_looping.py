from fastapi.testclient import TestClient
from backend.main import app
from backend import state
from unittest.mock import MagicMock
import pytest

client = TestClient(app)

def test_loop_control():
    # Mock project
    mock_project = MagicMock()
    mock_project.loop_mode = "none"
    def set_mode(m):
        mock_project.loop_mode = m
    mock_project.set_loop_mode.side_effect = set_mode
    state.project = mock_project

    # Test set loop mode
    response = client.post("/playback/loop", json={"mode": "bar"})
    assert response.status_code == 200
    assert response.json()["loop_mode"] == "bar"
    mock_project.set_loop_mode.assert_called_once_with("bar")

    # Cleanup
    state.project = None

def test_status_loop_info():
    # Mock project
    mock_project = MagicMock()
    mock_project.position = 10.5
    mock_project.duration = 60.0
    mock_project.backend._playing = False
    mock_project.backend._speed = 1.0
    mock_project.backend._volume = 1.0
    mock_project.audio_path.name = "test.wav"
    mock_project.flags = []
    mock_project.harmony_flags = []
    mock_project._dirty = False
    mock_project.backend._metronome_enabled = True
    mock_project.backend._click_gain = 0.3
    mock_project.loop_mode = "section"
    mock_project.get_loop_range.return_value = (10.0, 20.0)

    state.project = mock_project

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["loop_mode"] == "section"
    assert data["loop_range"] == [10.0, 20.0]

    # Cleanup
    state.project = None
