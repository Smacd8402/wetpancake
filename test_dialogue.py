from app.dialogue import ProspectState, generate_prospect_turn


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
