import pytest
from fastapi.testclient import TestClient
from backend.main import app

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
