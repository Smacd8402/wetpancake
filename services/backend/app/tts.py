class TTSService:
    def synthesize(self, text: str) -> bytes:
        if not text:
            return b""
        # Placeholder hook for Piper integration.
        return text.encode("utf-8")
