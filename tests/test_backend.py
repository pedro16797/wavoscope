import pytest
from fastapi.testclient import TestClient
from backend.main import app
import backend.main
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
    backend.main.project = mock_project

    response = client.post("/project/flags/insert_n", json={"left_idx": 0, "count": 3})
    assert response.status_code == 200
    # The endpoint calls project.insert_equi_spaced_flags(data.left_idx, data.left_idx + 1, data.count)
    mock_project.insert_equi_spaced_flags.assert_called_once_with(0, 1, 3)

    # Cleanup
    backend.main.project = None
