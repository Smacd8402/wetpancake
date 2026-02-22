import subprocess
import uuid
from pathlib import Path

RUNTIME_IO_DIR = Path(__file__).resolve().parents[1] / "data" / "runtime_io"
RUNTIME_IO_DIR.mkdir(parents=True, exist_ok=True)


class TTSService:
    def synthesize(self, text: str) -> bytes:
        if not text:
            return b""
        return text.encode("utf-8")


class PiperCliTTSService(TTSService):
    def __init__(self, command_template: str, voice_path: str):
        self.command_template = command_template
        self.voice_path = voice_path

    def synthesize(self, text: str) -> bytes:
        if not text:
            return b""
        if not self.command_template:
            raise RuntimeError("Piper command template is not configured")

        voice = Path(self.voice_path)
        if not voice.exists():
            raise RuntimeError("Piper voice file not found")

        token = str(uuid.uuid4())
        input_txt = RUNTIME_IO_DIR / f"{token}-input.txt"
        output_wav = RUNTIME_IO_DIR / f"{token}-output.wav"
        input_txt.write_text(text, encoding="utf-8")

        command = self.command_template.format(
            voice_path=str(voice),
            input_txt=str(input_txt),
            output_wav=str(output_wav),
        )
        proc = subprocess.run(command, shell=True, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"TTS command failed: {proc.stderr.strip()}")
        if not output_wav.exists():
            raise RuntimeError("TTS command succeeded but output WAV was not created")
        return output_wav.read_bytes()
