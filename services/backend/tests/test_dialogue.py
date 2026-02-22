from fastapi.testclient import TestClient

from app.dialogue import ProspectState, generate_prospect_turn
from app.main import app, ollama_client


def test_dialogue_returns_text_and_state_updates():
    state = ProspectState(trust=0.4, resistance=0.6)
    out = generate_prospect_turn(
        state=state,
        trainee_text="Can I get 30 seconds to explain why I called?",
        persona={"primary_objection": "busy"},
    )
    assert out.text
    assert 0.0 <= out.next_state.trust <= 1.0
    assert 0.0 <= out.next_state.resistance <= 1.0


def test_dialogue_endpoint_falls_back_when_ollama_unavailable(monkeypatch):
    client = TestClient(app)

    def _raise(_prompt: str) -> str:
        raise RuntimeError("llm unavailable")

    monkeypatch.setattr(ollama_client, "generate", _raise)

    response = client.post(
        "/dialogue/turn",
        json={
            "trust": 0.4,
            "resistance": 0.6,
            "trainee_text": "Can I get 30 seconds?",
            "primary_objection": "busy",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "I have a minute. What exactly are you offering?"
