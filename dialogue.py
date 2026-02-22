from dataclasses import dataclass
from typing import Protocol


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
            f"Prospect objection={objection}, trust={next_state.trust:.2f}, "
            f"resistance={next_state.resistance:.2f}. Respond briefly to: {trainee_text}"
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
