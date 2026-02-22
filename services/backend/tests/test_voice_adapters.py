from app.stt import STTService
from app.tts import TTSService


def test_voice_adapters_have_required_interfaces():
    assert hasattr(STTService, "transcribe_chunk")
    assert hasattr(TTSService, "synthesize")
