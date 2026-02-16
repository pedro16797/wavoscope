from fastapi.testclient import TestClient
from backend.main import app
from backend import state
import backend.routers.project
from unittest.mock import MagicMock

client = TestClient(app)

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"loaded": False}

def test_themes():
    response = client.get("/themes")
    assert response.status_code == 200
    themes = response.json()
    assert "dark" in themes
    assert themes["dark"]["accent"] == "#00aaff"

def test_insert_n_flags():
    # Mock project
    mock_project = MagicMock()
    mock_project.flags = [{"t": 0.0}, {"t": 1.0}]
    state.project = mock_project

    response = client.post("/project/flags/insert_n", json={"left_idx": 0, "count": 3})
    assert response.status_code == 200
    # The endpoint calls project.insert_equi_spaced_flags(data.left_idx, data.left_idx + 1, data.count)
    mock_project.insert_equi_spaced_flags.assert_called_once_with(0, 1, 3)

    # Cleanup
    state.project = None

def test_harmony_flags():
    # Mock project
    mock_project = MagicMock()
    mock_project.harmony_flags = [{"t": 0.5, "chord": {"root": "C", "quality": "M"}}]
    state.project = mock_project

    # Test add
    response = client.post("/project/harmony_flags", json={"t": 1.5, "chord": {"root": "G", "quality": "M"}})
    assert response.status_code == 200
    mock_project.add_harmony_flag.assert_called_once()

    # Test move
    response = client.post("/project/harmony_flags/move", json={"idx": 0, "t": 0.6})
    assert response.status_code == 200
    mock_project.move_harmony_flag.assert_called_once_with(0, 0.6)

    # Test delete
    response = client.delete("/project/harmony_flags/0")
    assert response.status_code == 200
    mock_project.remove_harmony_flag.assert_called_once_with(0)

    # Test analyze
    mock_project.backend._data = None # Trigger default in mock
    response = client.get("/project/analyze_chord?t=1.0")
    assert response.status_code == 200
    assert "root" in response.json()

    # Cleanup
    state.project = None

def test_open_project(tmp_path):
    # Create a dummy audio file
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"dummy audio content")

    # Mock Project to avoid actual audio loading issues in test environment
    with MagicMock() as mock_project_class:
        # We need to patch where it's used (in the router)
        backend.routers.project.Project = mock_project_class
        response = client.post("/project/open", json={"path": str(audio_file)})
        assert response.status_code == 200
        assert response.json()["filename"] == "test.wav"
