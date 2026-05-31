import time
from typing import Any

import numpy as np

from app.models.audio_chunk import AudioChunk
from app.models.transcription_result import TranscriptionResult, TranscriptionSegment
from app.providers.base import ASRProvider
from app.utils.audio import chunk_to_float32_array


class FastWhisperProvider(ASRProvider):
    """Fast-whisper transcription via faster-whisper (CTranslate2)."""

    ENGINE_NAME = "fast-whisper"

    def __init__(
        self,
        model_name: str,
        device: str,
        language: str,
        compute_type: str,
        initial_prompt: str | None = None,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._language = language
        self._compute_type = compute_type
        self._initial_prompt = initial_prompt
        self._model: Any = None

    def preload(self) -> None:
        from faster_whisper import WhisperModel

        self._model = WhisperModel(
            self._model_name,
            device=self._device,
            compute_type=self._compute_type,
        )

    def health_check(self) -> bool:
        return self._model is not None

    def get_metadata(self) -> dict[str, str]:
        return {
            "engine": self.ENGINE_NAME,
            "model_version": self._model_name,
            "device": self._device,
        }

    def transcribe(self, chunk: AudioChunk) -> TranscriptionResult:
        if not self.health_check():
            raise RuntimeError("Fast-whisper model is not loaded. Call preload() first.")

        started_at = time.perf_counter()
        audio = chunk_to_float32_array(chunk)

        if audio.size == 0:
            return self._empty_result(chunk, started_at)

        transcribe_kwargs: dict[str, Any] = {
            "language": self._language,
            "vad_filter": True,
        }
        if self._initial_prompt:
            transcribe_kwargs["initial_prompt"] = self._initial_prompt

        segments_iter, info = self._model.transcribe(audio, **transcribe_kwargs)

        segments: list[TranscriptionSegment] = []
        text_parts: list[str] = []
        confidences: list[float] = []

        for segment in segments_iter:
            segment_text = segment.text.strip()
            if not segment_text:
                continue

            confidence = self._segment_confidence(segment)
            segments.append(
                TranscriptionSegment(
                    text=segment_text,
                    start_ms=segment.start * 1000,
                    end_ms=segment.end * 1000,
                    confidence=confidence,
                )
            )
            text_parts.append(segment_text)
            if confidence is not None:
                confidences.append(confidence)

        full_text = " ".join(text_parts).strip()
        latency_ms = (time.perf_counter() - started_at) * 1000
        avg_confidence = float(np.mean(confidences)) if confidences else None

        metadata = self.get_metadata()
        return TranscriptionResult(
            text=full_text,
            engine=metadata["engine"],
            model_version=metadata["model_version"],
            device=metadata["device"],
            latency_ms=latency_ms,
            session_id=chunk.session_id,
            sequence=chunk.sequence,
            confidence=avg_confidence or getattr(info, "language_probability", None),
            segments=segments,
            timestamp_ms=chunk.timestamp_ms,
        )

    def _empty_result(
        self, chunk: AudioChunk, started_at: float
    ) -> TranscriptionResult:
        metadata = self.get_metadata()
        latency_ms = (time.perf_counter() - started_at) * 1000
        return TranscriptionResult(
            text="",
            engine=metadata["engine"],
            model_version=metadata["model_version"],
            device=metadata["device"],
            latency_ms=latency_ms,
            session_id=chunk.session_id,
            sequence=chunk.sequence,
            timestamp_ms=chunk.timestamp_ms,
        )

    @staticmethod
    def _segment_confidence(segment: Any) -> float | None:
        if not getattr(segment, "words", None):
            return None

        word_probs = [
            word.probability
            for word in segment.words
            if getattr(word, "probability", None) is not None
        ]
        if not word_probs:
            return None

        return float(np.mean(word_probs))
