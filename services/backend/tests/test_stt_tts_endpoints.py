from fastapi.testclient import TestClient

from app.main import app


def test_stt_transcribe_endpoint_returns_text():
    client = TestClient(app)
    files = {"audio": ("sample.wav", b"RIFFFAKEWAV", "audio/wav")}
    resp = client.post("/stt/transcribe", files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert "text" in body


def test_tts_synthesize_endpoint_returns_audio_bytes():
    client = TestClient(app)
    resp = client.post("/tts/synthesize", json={"text": "hello"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/wav"
    assert len(resp.content) > 0
