from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class TranscriptionSegment:
    """Word-level segment with timing and confidence."""

    text: str
    start_ms: float
    end_ms: float
    confidence: Optional[float] = None


@dataclass
class TranscriptionResult:
    """Standard output contract for all ASR providers."""

    text: str
    engine: str
    model_version: str
    device: str
    latency_ms: float
    session_id: str
    sequence: int
    confidence: Optional[float] = None
    segments: list[TranscriptionSegment] = field(default_factory=list)
    timestamp_ms: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
