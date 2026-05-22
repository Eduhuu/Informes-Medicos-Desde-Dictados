from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AudioChunk:
    """Input contract for a single audio fragment."""

    data: bytes
    session_id: str
    sequence: int
    timestamp_ms: Optional[int] = None
    ground_truth_text: Optional[str] = None
    sample_rate_hz: int = 16000
    channels: int = 1
    sample_width_bytes: int = 2
