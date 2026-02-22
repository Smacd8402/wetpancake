from fastapi.testclient import TestClient
from app.main import app


def test_created_session_is_persisted():
    client = TestClient(app)
    created = client.post("/sessions", json={"duration_minutes": 8}).json()
    fetched = client.get(f"/sessions/{created['session_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["session_id"] == created["session_id"]
