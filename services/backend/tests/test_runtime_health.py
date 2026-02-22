from unittest.mock import patch

from app.runtime_health import check_runtime_dependencies


def test_runtime_health_reports_unavailable_dependencies():
    with patch("app.runtime_health._check_ollama", return_value=(False, "down")):
        report = check_runtime_dependencies(
            ollama_base_url="http://127.0.0.1:11434",
            ollama_model="mistral:7b",
            whisper_cmd_template="",
            piper_cmd_template="",
            piper_voice_path="",
        )

    assert report["ok"] is False
    assert report["checks"]["ollama"]["ok"] is False
