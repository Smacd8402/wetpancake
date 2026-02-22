from unittest.mock import patch

import pytest

from app.stt import WhisperCliSTTService


def test_stt_cli_uses_stdout_transcript_when_available():
    svc = WhisperCliSTTService('whisper --input "{input_wav}"')

    class _Proc:
        returncode = 0
        stdout = "hello there\n"
        stderr = ""

    with patch("subprocess.run", return_value=_Proc()):
        text = svc.transcribe_chunk(b"RIFFfakewav")

    assert text == "hello there"


def test_stt_cli_raises_when_command_fails():
    svc = WhisperCliSTTService('whisper --input "{input_wav}"')

    class _Proc:
        returncode = 1
        stdout = ""
        stderr = "boom"

    with patch("subprocess.run", return_value=_Proc()):
        with pytest.raises(RuntimeError, match="STT command failed"):
            svc.transcribe_chunk(b"RIFFfakewav")
