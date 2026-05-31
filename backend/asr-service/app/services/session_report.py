import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from app.constants.messages import (
    REPORT_LABEL_TIMESTAMP_MS,
    REPORT_LABEL_TIMESTAMP_UNKNOWN,
    REPORT_NER_ENTITY_LINE,
    REPORT_SECTION_TIMINGS,
    REPORT_TIMING_ASR,
    REPORT_TIMING_NER,
    REPORT_TIMING_SNOMED,
    REPORT_TIMING_TOTAL,
    REPORT_NER_NO_ENTITIES,
    REPORT_SECTION_CALL,
    REPORT_SECTION_NER,
    REPORT_SECTION_SNOMED,
    REPORT_SECTION_TRANSCRIPTION,
    REPORT_SESSION_HEADER,
    REPORT_SESSION_STARTED,
    REPORT_SNOMED_ACTIVE_LINE,
    REPORT_SNOMED_CONCEPT_LINE,
    REPORT_SNOMED_DEFINITION_LINE,
    REPORT_SNOMED_ENTITY_HEADER,
    REPORT_SNOMED_ERROR,
    REPORT_SNOMED_FSN_LINE,
    REPORT_SNOMED_NOT_APPLICABLE,
    REPORT_SNOMED_NO_MATCH,
    REPORT_SNOMED_PT_LINE,
    REPORT_SNOMED_TOTAL_HINT,
    REPORT_TRANSCRIPTION_EMPTY,
    REPORT_WARNING_PREFIX,
)
from app.models.chunk_processing_timings import ChunkProcessingTimings
from app.models.snomed import EnrichedEntity
from app.services.pln_labels import pln_source_label
from shared.constants.ReportConstants import (
    MILLISECONDS_PER_SECOND,
    REPORT_FILENAME_PREFIX,
    REPORT_FILENAME_SUFFIX,
    REPORT_SECTION_SEPARATOR,
    REPORT_SUBSECTION_SEPARATOR,
    REPORT_TIMING_DECIMAL_PLACES,
)

_SAFE_SESSION_ID_PATTERN = re.compile(r"[^\w\-]+")


class SessionReportWriter:
    """Appends one section per /transcribe call to a text file per session."""

    def __init__(self, reports_dir: Path, *, enabled: bool = True) -> None:
        self._reports_dir = reports_dir
        self._enabled = enabled
        self._locks: dict[str, threading.Lock] = {}
        if enabled:
            reports_dir.mkdir(parents=True, exist_ok=True)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def append_call(
        self,
        *,
        session_id: str,
        sequence: int,
        timestamp_ms: int | None,
        transcription_text: str,
        enriched_entities: list[EnrichedEntity],
        timings: ChunkProcessingTimings,
        warning: str | None = None,
    ) -> None:
        if not self._enabled:
            return

        report_path = self._report_path(session_id)
        block = self._format_call_block(
            session_id=session_id,
            sequence=sequence,
            timestamp_ms=timestamp_ms,
            transcription_text=transcription_text,
            enriched_entities=enriched_entities,
            timings=timings,
            warning=warning,
            is_new_file=not report_path.exists(),
        )

        lock = self._lock_for(session_id)
        with lock:
            with report_path.open("a", encoding="utf-8") as report_file:
                report_file.write(block)

    def _lock_for(self, session_id: str) -> threading.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = threading.Lock()
        return self._locks[session_id]

    def _report_path(self, session_id: str) -> Path:
        safe_id = _SAFE_SESSION_ID_PATTERN.sub("_", session_id).strip("_") or "default"
        filename = f"{REPORT_FILENAME_PREFIX}{safe_id}{REPORT_FILENAME_SUFFIX}"
        return self._reports_dir / filename

    def _format_call_block(
        self,
        *,
        session_id: str,
        sequence: int,
        timestamp_ms: int | None,
        transcription_text: str,
        enriched_entities: list[EnrichedEntity],
        timings: ChunkProcessingTimings,
        warning: str | None,
        is_new_file: bool,
    ) -> str:
        lines: list[str] = []

        if is_new_file:
            started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            lines.extend(
                [
                    REPORT_SECTION_SEPARATOR,
                    REPORT_SESSION_HEADER.format(session_id=session_id),
                    REPORT_SESSION_STARTED.format(timestamp=started_at),
                    REPORT_SECTION_SEPARATOR,
                    "",
                ],
            )

        lines.extend(
            [
                REPORT_SECTION_SEPARATOR,
                REPORT_SECTION_CALL.format(sequence=sequence),
            ],
        )
        if timestamp_ms is not None:
            lines.append(
                REPORT_LABEL_TIMESTAMP_MS.format(timestamp_ms=timestamp_ms),
            )
        else:
            lines.append(REPORT_LABEL_TIMESTAMP_UNKNOWN)

        lines.extend(
            [
                "",
                REPORT_SECTION_TIMINGS,
                REPORT_SUBSECTION_SEPARATOR,
                REPORT_TIMING_TOTAL.format(
                    duration_s=self._format_duration_seconds(timings.total_ms),
                ),
                REPORT_TIMING_ASR.format(
                    duration_s=self._format_duration_seconds(timings.asr_ms),
                ),
                REPORT_TIMING_NER.format(
                    duration_s=self._format_duration_seconds(timings.ner_ms),
                ),
                REPORT_TIMING_SNOMED.format(
                    duration_s=self._format_duration_seconds(timings.snomed_ms),
                ),
            ],
        )

        lines.extend(["", REPORT_SECTION_TRANSCRIPTION, REPORT_SUBSECTION_SEPARATOR])
        if transcription_text.strip():
            lines.append(transcription_text.strip())
        else:
            lines.append(REPORT_TRANSCRIPTION_EMPTY)

        if warning:
            lines.append(
                REPORT_WARNING_PREFIX.format(message=warning),
            )

        lines.extend(["", REPORT_SECTION_NER, REPORT_SUBSECTION_SEPARATOR])
        if enriched_entities:
            for index, entity in enumerate(enriched_entities, start=1):
                lines.append(
                    REPORT_NER_ENTITY_LINE.format(
                        index=index,
                        word=entity.word,
                        entity_group=entity.entity_group,
                        pln_source_label=pln_source_label(entity.pln_source),
                        score=entity.score,
                        start=entity.start,
                        end=entity.end,
                    ),
                )
        else:
            lines.append(REPORT_NER_NO_ENTITIES)

        lines.extend(["", REPORT_SECTION_SNOMED, REPORT_SUBSECTION_SEPARATOR])
        if enriched_entities:
            for index, entity in enumerate(enriched_entities, start=1):
                lines.extend(
                    self._format_snomed_lines(index=index, entity=entity),
                )
        else:
            lines.append(REPORT_SNOMED_NOT_APPLICABLE)

        lines.append("")
        return "\n".join(lines) + "\n"

    def _format_duration_seconds(self, duration_ms: float) -> str:
        duration_s = duration_ms / MILLISECONDS_PER_SECOND
        return f"{duration_s:.{REPORT_TIMING_DECIMAL_PLACES}f}"

    def _format_snomed_lines(
        self,
        *,
        index: int,
        entity: EnrichedEntity,
    ) -> list[str]:
        lines = [REPORT_SNOMED_ENTITY_HEADER.format(index=index, word=entity.word)]
        snomed = entity.snomed

        if snomed.error:
            lines.append(REPORT_SNOMED_ERROR.format(error=snomed.error))
            return lines

        if snomed.total == 0 or not snomed.items:
            lines.append(REPORT_SNOMED_NO_MATCH)
            return lines

        concept = snomed.items[0]
        lines.extend(
            [
                REPORT_SNOMED_CONCEPT_LINE.format(concept_id=concept.conceptId),
                REPORT_SNOMED_PT_LINE.format(
                    term=concept.pt.term,
                    lang=concept.pt.lang,
                ),
                REPORT_SNOMED_FSN_LINE.format(
                    term=concept.fsn.term,
                    lang=concept.fsn.lang,
                ),
                REPORT_SNOMED_ACTIVE_LINE.format(active=concept.active),
                REPORT_SNOMED_DEFINITION_LINE.format(
                    status=concept.definitionStatus,
                ),
            ],
        )
        if snomed.total > 1:
            lines.append(
                REPORT_SNOMED_TOTAL_HINT.format(total=snomed.total),
            )
        return lines
