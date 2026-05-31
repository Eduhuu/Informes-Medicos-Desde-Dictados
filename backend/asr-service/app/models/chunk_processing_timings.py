from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkProcessingTimings:
    """Wall-clock durations for one /transcribe chunk, in milliseconds."""

    asr_ms: float
    ner_ms: float
    snomed_ms: float
    total_ms: float
