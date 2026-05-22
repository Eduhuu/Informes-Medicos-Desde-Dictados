from abc import ABC, abstractmethod

from app.models.audio_chunk import AudioChunk
from app.models.transcription_result import TranscriptionResult


class ASRProvider(ABC):
    """Strategy interface for interchangeable transcription engines."""

    @abstractmethod
    def transcribe(self, chunk: AudioChunk) -> TranscriptionResult:
        """Transcribe a single audio chunk."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the engine is loaded and ready."""

    @abstractmethod
    def get_metadata(self) -> dict[str, str]:
        """Return engine name, model version and device for metrics."""

    def preload(self) -> None:
        """Optional hook to load models at startup (default: no-op)."""
