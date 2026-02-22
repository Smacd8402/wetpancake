import json
from dataclasses import dataclass
from typing import Protocol
from urllib import request
from urllib.error import URLError


@dataclass(frozen=True)
class ProspectState:
    trust: float
    resistance: float


@dataclass(frozen=True)
class DialogueTurn:
    text: str
    next_state: ProspectState


class LocalLLMClient(Protocol):
    def generate(self, prompt: str) -> str: ...


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.35},
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned invalid JSON") from exc

        response_text = body.get("response")
        if not response_text:
            raise RuntimeError("Ollama response missing 'response' field")
        return str(response_text).strip()


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def generate_prospect_turn(
    state: ProspectState,
    trainee_text: str,
    persona: dict,
    llm_client: LocalLLMClient | None = None,
) -> DialogueTurn:
    objection = persona.get("primary_objection", "busy")
    lowered = trainee_text.lower()

    trust_delta = 0.1 if "30 seconds" in lowered or "quick" in lowered else -0.05
    resistance_delta = -0.12 if "value" in lowered or "help" in lowered else 0.04

    next_state = ProspectState(
        trust=_clamp(state.trust + trust_delta),
        resistance=_clamp(state.resistance + resistance_delta),
    )

    if llm_client is not None:
        prompt = (
            "You are a realistic B2B cold call prospect. "
            f"Current objection style: {objection}. "
            f"Trust={next_state.trust:.2f}, resistance={next_state.resistance:.2f}. "
            "Reply in one short spoken sentence, natural and slightly skeptical.\n"
            f"Trainee said: {trainee_text}"
        )
        text = llm_client.generate(prompt)
    else:
        if objection == "busy":
            text = "I have a minute. What exactly are you offering?"
        elif objection == "no_budget":
            text = "We are not allocating budget right now."
        else:
            text = "I am listening, but keep it short."

    return DialogueTurn(text=text, next_state=next_state)
