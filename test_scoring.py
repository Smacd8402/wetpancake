from app.scoring import score_session


def test_score_session_returns_dimension_scores_and_total():
    report = score_session(
        transcript=[{"speaker": "trainee", "text": "Can I get 30 seconds?"}],
        outcomes={"close_attempt": True},
    )
    assert "total_score" in report
    assert "dimensions" in report
    assert "misses" in report
