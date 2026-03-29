import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import state

client = TestClient(app)

def test_get_remote_url():
    state.port = 1234
    response = client.get("/config/remote-url")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data["url"].endswith(":1234")
    assert data["url"].startswith("http://")

def test_config_remote_access():
    # Test getting config
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "remote_access" in data

    # Test updating config
    response = client.post("/config", json={"remote_access": True})
    assert response.status_code == 200

    response = client.get("/config")
    assert response.status_code == 200
    assert response.json()["remote_access"] is True

    # Cleanup
    client.post("/config", json={"remote_access": False})
