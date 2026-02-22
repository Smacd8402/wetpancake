# Local Model Setup

## Planned Local Runtime
- LLM: local Ollama-compatible model endpoint
- STT: Faster-Whisper
- TTS: Piper

## Current Status
- Backend includes adapter contracts only (`app/dialogue.py`, `app/stt.py`, `app/tts.py`).
- Swap adapter internals to real model runners on this machine.

## Next Integration Steps
1. Add concrete STT transcription in `app/stt.py`.
2. Add concrete TTS synthesis in `app/tts.py`.
3. Replace dialogue fallback with local model in `app/dialogue.py`.
4. Add runtime health checks for all model backends in `scripts/check.ps1`.
