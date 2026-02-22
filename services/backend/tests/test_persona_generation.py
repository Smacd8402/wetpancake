from app.persona import PersonaGenerator


def test_persona_generator_avoids_recent_primary_objection():
    gen = PersonaGenerator()
    recent = [{"primary_objection": "no_budget"}]
    persona = gen.generate(seed=1234, recent_sessions=recent)
    assert persona.primary_objection != "no_budget"
