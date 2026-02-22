from unittest.mock import patch

import pytest

from app.dialogue import OllamaClient


def test_ollama_client_parses_response_text():
    client = OllamaClient(base_url="http://127.0.0.1:11434", model="mistral:7b")

    class _Resp:
        status = 200

        def read(self):
            return b'{"response":"prospect reply"}'

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    with patch("urllib.request.urlopen", return_value=_Resp()):
        out = client.generate("prompt")

    assert out == "prospect reply"


def test_ollama_client_raises_on_bad_payload():
    client = OllamaClient(base_url="http://127.0.0.1:11434", model="mistral:7b")

    class _Resp:
        status = 200

        def read(self):
            return b'{"not_response":"x"}'

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    with patch("urllib.request.urlopen", return_value=_Resp()):
        with pytest.raises(RuntimeError, match="missing 'response'"):
            client.generate("prompt")
