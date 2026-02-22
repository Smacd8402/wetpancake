from collections import Counter


def _clip(score: float) -> int:
    return int(max(0, min(100, round(score))))


def score_session(transcript: list[dict], outcomes: dict) -> dict:
    trainee_turns = [t for t in transcript if t.get("speaker") == "trainee"]
    trainee_words = sum(len((t.get("text") or "").split()) for t in trainee_turns)
    total_words = sum(len((t.get("text") or "").split()) for t in transcript) or 1
    talk_ratio = trainee_words / total_words

    dimensions = {
        "opener_clarity": _clip(65 + (10 if trainee_turns else -20)),
        "rapport_tone": _clip(60 + (5 if talk_ratio <= 0.65 else -10)),
        "discovery_depth": _clip(50 + min(20, len(trainee_turns) * 3)),
        "objection_handling": _clip(55 + (10 if "objection_resolved" in outcomes else 0)),
        "value_articulation": _clip(58 + (10 if outcomes.get("value_statement") else 0)),
        "close_quality": _clip(50 + (20 if outcomes.get("close_attempt") else -10)),
        "talk_listen_balance": _clip(100 - abs(0.5 - talk_ratio) * 120),
    }

    weights = {
        "opener_clarity": 0.15,
        "rapport_tone": 0.12,
        "discovery_depth": 0.18,
        "objection_handling": 0.16,
        "value_articulation": 0.14,
        "close_quality": 0.15,
        "talk_listen_balance": 0.10,
    }

    total_score = _clip(sum(dimensions[k] * w for k, w in weights.items()))

    misses = []
    if dimensions["discovery_depth"] < 65:
        misses.append("Ask one additional pain-focused discovery question.")
    if dimensions["close_quality"] < 65:
        misses.append("Make a direct next-step close before ending the call.")
    if dimensions["talk_listen_balance"] < 65:
        misses.append("Reduce monologue length and invite prospect responses earlier.")
    if not misses:
        misses.append("Solid execution. Next improvement: tighten opener in first 10 seconds.")

    return {
        "total_score": total_score,
        "dimensions": dimensions,
        "misses": misses[:3],
        "replacement_phrasing": {
            "actual": "Can I get 30 seconds?",
            "stronger": "I called because teams like yours are cutting wasted follow-up time. Worth 30 seconds?",
        },
    }
