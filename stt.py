class STTService:
    def transcribe_chunk(self, pcm_bytes: bytes) -> str:
        if not pcm_bytes:
            return ""
        # Placeholder hook for Faster-Whisper integration.
        return "[transcript_pending]"
