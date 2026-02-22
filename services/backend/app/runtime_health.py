import json
import shutil
from pathlib import Path
from urllib import request
from urllib.error import URLError


def _check_ollama(base_url: str, model: str) -> tuple[bool, str]:
    try:
        with request.urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except URLError as exc:
        return (False, f"unreachable: {exc}")
    except json.JSONDecodeError:
        return (False, "invalid JSON from /api/tags")

    names = {item.get("name", "") for item in data.get("models", [])}
    if model not in names:
        return (False, f"model '{model}' not installed")
    return (True, "ok")


def _extract_command_binary(command_template: str) -> str:
    if not command_template.strip():
        return ""
    return command_template.strip().split()[0].strip('"')


def check_runtime_dependencies(
    ollama_base_url: str,
    ollama_model: str,
    whisper_cmd_template: str,
    piper_cmd_template: str,
    piper_voice_path: str,
) -> dict:
    checks: dict[str, dict[str, object]] = {}

    ok, detail = _check_ollama(ollama_base_url, ollama_model)
    checks["ollama"] = {"ok": ok, "detail": detail}

    whisper_bin = _extract_command_binary(whisper_cmd_template)
    whisper_ok = bool(whisper_bin) and shutil.which(whisper_bin) is not None
    checks["whisper"] = {
        "ok": whisper_ok,
        "detail": "ok" if whisper_ok else "command not found or template missing",
    }

    piper_bin = _extract_command_binary(piper_cmd_template)
    piper_ok = bool(piper_bin) and shutil.which(piper_bin) is not None
    checks["piper"] = {
        "ok": piper_ok,
        "detail": "ok" if piper_ok else "command not found or template missing",
    }

    voice_ok = bool(piper_voice_path) and Path(piper_voice_path).exists()
    checks["piper_voice"] = {
        "ok": voice_ok,
        "detail": "ok" if voice_ok else "voice file path does not exist",
    }

    overall_ok = all(bool(v["ok"]) for v in checks.values())
    return {"ok": overall_ok, "checks": checks}
