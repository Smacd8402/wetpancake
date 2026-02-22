import importlib
import os


def test_main_loads_env_from_repo_root(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.setenv("DOTENV_PATH", "")

    import app.main as main_module
    importlib.reload(main_module)

    assert os.getenv("OLLAMA_MODEL")
