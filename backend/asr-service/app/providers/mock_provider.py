import time

from app.models.audio_chunk import AudioChunk
from app.models.transcription_result import TranscriptionResult
from app.providers.base import ASRProvider


class MockProvider(ASRProvider):
    """Lightweight provider for local development without GPU/model downloads."""

    ENGINE_NAME = "mock"
    MODEL_VERSION = "mock-v1"

    def __init__(self, device: str = "cpu") -> None:
        self._device = device
        self._ready = False

    def preload(self) -> None:
        self._ready = True

    def health_check(self) -> bool:
        return self._ready

    def get_metadata(self) -> dict[str, str]:
        return {
            "engine": self.ENGINE_NAME,
            "model_version": self.MODEL_VERSION,
            "device": self._device,
        }

    def transcribe(self, chunk: AudioChunk) -> TranscriptionResult:
        if not self.health_check():
            raise RuntimeError("Mock provider is not ready. Call preload() first.")

        started_at = time.perf_counter()
        latency_ms = (time.perf_counter() - started_at) * 1000
        metadata = self.get_metadata()

        if chunk.ground_truth_text:
            text = chunk.ground_truth_text
        elif len(chunk.data) > 0:
            text = f"[mock] fragmento {chunk.sequence} recibido"
        else:
            text = ""

        return TranscriptionResult(
            text=text,
            engine=metadata["engine"],
            model_version=metadata["model_version"],
            device=metadata["device"],
            latency_ms=latency_ms,
            session_id=chunk.session_id,
            sequence=chunk.sequence,
            confidence=1.0 if text else None,
            timestamp_ms=chunk.timestamp_ms,
        )
