from pathlib import Path
from unittest.mock import patch
import uuid

import pytest

from app.tts import PiperCliTTSService


def test_tts_cli_returns_output_wav_bytes():
    test_dir = Path(".runtime_test") / str(uuid.uuid4())
    test_dir.mkdir(parents=True, exist_ok=True)
    voice = test_dir / "voice.onnx"
    voice.write_text("voice", encoding="utf-8")

    svc = PiperCliTTSService(
        command_template='piper --model "{voice_path}" --input_file "{input_txt}" --output_file "{output_wav}"',
        voice_path=str(voice),
    )

    class _Proc:
        returncode = 0
        stdout = ""
        stderr = ""

    def _fake_run(command, shell, capture_output, text):
        out_path = command.split('"')[-2]
        Path(out_path).write_bytes(b"WAVDATA")
        return _Proc()

    with patch("subprocess.run", side_effect=_fake_run):
        out = svc.synthesize("hello")

    assert out == b"WAVDATA"


def test_tts_cli_raises_when_voice_missing():
    svc = PiperCliTTSService(command_template='piper --model "{voice_path}"', voice_path=".runtime_test/missing.onnx")

    with pytest.raises(RuntimeError, match="Piper voice file not found"):
        svc.synthesize("hello")
