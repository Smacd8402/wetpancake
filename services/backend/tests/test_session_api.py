from fastapi.testclient import TestClient
from app.main import app


def test_create_session_returns_id_and_seed():
    client = TestClient(app)
    resp = client.post("/sessions", json={"duration_minutes": 8})
    assert resp.status_code == 201
    body = resp.json()
    assert "session_id" in body
    assert "seed" in body
