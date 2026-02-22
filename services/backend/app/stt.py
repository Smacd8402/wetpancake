import subprocess
import uuid
from pathlib import Path

RUNTIME_IO_DIR = Path(__file__).resolve().parents[1] / "data" / "runtime_io"
RUNTIME_IO_DIR.mkdir(parents=True, exist_ok=True)


class STTService:
    def transcribe_chunk(self, pcm_bytes: bytes) -> str:
        if not pcm_bytes:
            return ""
        return "[transcript_pending]"


class WhisperCliSTTService(STTService):
    def __init__(self, command_template: str):
        self.command_template = command_template

    def transcribe_chunk(self, pcm_bytes: bytes) -> str:
        if not self.command_template:
            raise RuntimeError("Whisper command template is not configured")
        if not pcm_bytes:
            return ""

        token = str(uuid.uuid4())
        input_wav = RUNTIME_IO_DIR / f"{token}-input.wav"
        output_txt = RUNTIME_IO_DIR / f"{token}-output.txt"
        input_wav.write_bytes(pcm_bytes)

        command = self.command_template.format(
            input_wav=str(input_wav),
            output_txt=str(output_txt),
            output_dir=str(RUNTIME_IO_DIR),
        )
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=RUNTIME_IO_DIR,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"STT command failed: {proc.stderr.strip()}")

        if output_txt.exists():
            text = output_txt.read_text(encoding="utf-8").strip()
            if text:
                return text
        alt_txt = RUNTIME_IO_DIR / f"{input_wav.stem}.txt"
        if alt_txt.exists():
            text = alt_txt.read_text(encoding="utf-8").strip()
            if text:
                return text

        stdout_text = proc.stdout.strip()
        if stdout_text:
            return stdout_text

        raise RuntimeError("STT command succeeded but returned no transcript")
