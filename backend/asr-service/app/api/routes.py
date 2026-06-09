import time
from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.constants.messages import (
    MSG_CONCEPT_MAP_UNAVAILABLE,
    MSG_FHIR_DISABLED,
    MSG_FHIR_UNAVAILABLE,
    MSG_HEALTH_OK,
    MSG_HEALTH_UNAVAILABLE,
    MSG_INVALID_SEQUENCE,
    MSG_LLM_DISABLED,
    MSG_LLM_REPORT_NOT_FOUND,
    MSG_LLM_UNAVAILABLE,
    MSG_MISSING_AUDIO,
    MSG_SERVICE_READY,
    MSG_TRANSCRIPTION_EMPTY,
)
from app.models.audio_chunk import AudioChunk
from app.models.chunk_processing_timings import ChunkProcessingTimings
from app.models.snomed import EnrichedEntity
from app.providers.base import ASRProvider
from app.services.entity_enrichment import enrich_entities
from app.services.fhir_concept_map_client import FhirConceptMapClient
from app.services.fhir_report_generator import FhirReportGenerator
from app.services.llm_report_generator import LlmReportGenerator
from app.services.pln_orchestrator import PlnOrchestrator
from app.services.session_report import SessionReportWriter
from app.services.transcription_console_log import log_transcription_call_to_console
from app.snomed.base import SnomedClient
from shared.constants.AsrConstants import (
    DEFAULT_CHANNELS,
    DEFAULT_SAMPLE_RATE_HZ,
    DEFAULT_SAMPLE_WIDTH_BYTES,
    HEADER_SEQUENCE,
    HEADER_SESSION_ID,
    HEADER_TIMESTAMP,
    TRANSCRIBE_RESPONSE_KEY_ENTITIES,
)
from shared.constants.FhirReportConstants import FHIR_REQUEST_BODY_KEY_ENTITIES
from shared.constants.PlnConstants import (
    NER_GROUP_SPACE_TOLERANCE,
    NER_KEY_END,
    NER_KEY_ENTITY_GROUP,
    NER_KEY_SCORE,
    NER_KEY_START,
    NER_KEY_WORD,
)

router = APIRouter()


class GenerateFhirReportRequest(BaseModel):
    entities: list[dict[str, Any]] = Field(
        default_factory=list,
        alias=FHIR_REQUEST_BODY_KEY_ENTITIES,
    )

    model_config = {"populate_by_name": True}


def _get_provider(request: Request) -> ASRProvider:
    provider = getattr(request.app.state, "asr_provider", None)
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_HEALTH_UNAVAILABLE,
        )
    return provider


def _get_pln_orchestrator(request: Request) -> PlnOrchestrator:
    orchestrator = getattr(request.app.state, "pln_orchestrator", None)
    if orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_HEALTH_UNAVAILABLE,
        )
    return orchestrator


def _get_session_report_writer(request: Request) -> SessionReportWriter:
    writer = getattr(request.app.state, "session_report_writer", None)
    if writer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_HEALTH_UNAVAILABLE,
        )
    return writer


def _get_snomed_client(request: Request) -> SnomedClient:
    client = getattr(request.app.state, "snomed_client", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_HEALTH_UNAVAILABLE,
        )
    return client


def _get_llm_report_generator(request: Request) -> LlmReportGenerator:
    generator = getattr(request.app.state, "llm_report_generator", None)
    if generator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_LLM_UNAVAILABLE,
        )
    return generator


def _get_fhir_report_generator(request: Request) -> FhirReportGenerator:
    generator = getattr(request.app.state, "fhir_report_generator", None)
    if generator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_FHIR_UNAVAILABLE,
        )
    return generator


def _get_concept_map_client(request: Request) -> FhirConceptMapClient:
    client = getattr(request.app.state, "fhir_concept_map_client", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_CONCEPT_MAP_UNAVAILABLE,
        )
    return client


async def _translate_entities(
    entities: list[EnrichedEntity],
    client: FhirConceptMapClient,
) -> list[EnrichedEntity]:
    """Translate each entity through the three-step fallback chain:
    primary ConceptMap → fallback ConceptMap → ValueSet $expand.
    """
    translated: list[EnrichedEntity] = []
    for entity in entities:
        concept_id = entity.snomed.items[0].conceptId if entity.snomed.items else None
        translation = await client.translate(
            concept_id=concept_id or "",
            term=entity.word,
        )
        entity.concept_map = translation
        translated.append(entity)
    return translated


def _parse_sequence(raw_sequence: str | None) -> int:
    if raw_sequence is None:
        return 0

    try:
        return int(raw_sequence)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=MSG_INVALID_SEQUENCE,
        ) from exc


def _parse_timestamp(raw_timestamp: str | None) -> int | None:
    if raw_timestamp is None:
        return None

    try:
        return int(raw_timestamp)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cabecera X-Timestamp inválida",
        ) from exc


def group_entities(ner_entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge consecutive entities that share the same label into a single entry.

    Entities separated by at most NER_GROUP_SPACE_TOLERANCE characters are
    treated as contiguous so that multi-token clinical terms such as
    "diabetes mellitus tipo 2" are forwarded to SNOMED as one concept instead
    of three separate lookups.
    """
    if not ner_entities:
        return []

    sorted_entities = sorted(ner_entities, key=lambda e: e[NER_KEY_START])
    grouped: list[dict[str, Any]] = []
    current = sorted_entities[0].copy()

    for next_entity in sorted_entities[1:]:
        same_label = current[NER_KEY_ENTITY_GROUP] == next_entity[NER_KEY_ENTITY_GROUP]
        contiguous = (next_entity[NER_KEY_START] - current[NER_KEY_END]) <= NER_GROUP_SPACE_TOLERANCE

        if same_label and contiguous:
            current[NER_KEY_WORD] += " " + next_entity[NER_KEY_WORD]
            current[NER_KEY_END] = next_entity[NER_KEY_END]
            current[NER_KEY_SCORE] = (current[NER_KEY_SCORE] + next_entity[NER_KEY_SCORE]) / 2
        else:
            grouped.append(current)
            current = next_entity.copy()

    grouped.append(current)
    return grouped


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": MSG_SERVICE_READY}


@router.get("/health")
async def health(request: Request) -> dict[str, object]:
    provider = _get_provider(request)
    is_healthy = provider.health_check()
    metadata = provider.get_metadata()

    return {
        "status": "ok" if is_healthy else "unavailable",
        "message": MSG_HEALTH_OK if is_healthy else MSG_HEALTH_UNAVAILABLE,
        "metadata": metadata,
    }


@router.get("/metadata")
async def metadata(request: Request) -> dict[str, str]:
    provider = _get_provider(request)
    return provider.get_metadata()

@router.post("/transcribe")
async def transcribe(
    request: Request,
    x_session_id: Annotated[str | None, Header(alias=HEADER_SESSION_ID)] = None,
    x_sequence: Annotated[str | None, Header(alias=HEADER_SEQUENCE)] = None,
    x_timestamp: Annotated[str | None, Header(alias=HEADER_TIMESTAMP)] = None,
) -> dict[str, object]:
    audio_data = await request.body()
    if not audio_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=MSG_MISSING_AUDIO,
        )

    chunk = AudioChunk(
        data=audio_data,
        session_id=x_session_id or "default",
        sequence=_parse_sequence(x_sequence),
        timestamp_ms=_parse_timestamp(x_timestamp),
        sample_rate_hz=DEFAULT_SAMPLE_RATE_HZ,
        channels=DEFAULT_CHANNELS,
        sample_width_bytes=DEFAULT_SAMPLE_WIDTH_BYTES,
    )

    chunk_started_at = time.perf_counter()

    provider = _get_provider(request)
    asr_started_at = time.perf_counter()
    result = provider.transcribe(chunk)
    asr_ms = (time.perf_counter() - asr_started_at) * 1000

    response = result.to_dict()
    warning: str | None = None
    enriched_entities = []
    ner_ms = 0.0
    snomed_ms = 0.0

    if not result.text:
        warning = MSG_TRANSCRIPTION_EMPTY
        response["warning"] = warning
        total_ms = (time.perf_counter() - chunk_started_at) * 1000
        timings = ChunkProcessingTimings(
            asr_ms=asr_ms,
            ner_ms=ner_ms,
            snomed_ms=snomed_ms,
            total_ms=total_ms,
        )
        report_writer = _get_session_report_writer(request)
        if report_writer.enabled:
            report_writer.append_call(
                session_id=chunk.session_id,
                sequence=chunk.sequence,
                timestamp_ms=chunk.timestamp_ms,
                transcription_text=result.text,
                enriched_entities=enriched_entities,
                timings=timings,
                warning=warning,
            )
        response[TRANSCRIBE_RESPONSE_KEY_ENTITIES] = [
            entity.to_dict() for entity in enriched_entities
        ]
        return response

    pln_orchestrator = _get_pln_orchestrator(request)
    ner_started_at = time.perf_counter()
    ner_entities = await pln_orchestrator.process_text(result.text)
    ner_ms = (time.perf_counter() - ner_started_at) * 1000


    grouped_entities = group_entities(ner_entities)

    snomed_client = _get_snomed_client(request)
    snomed_started_at = time.perf_counter()
    enriched_entities = enrich_entities(grouped_entities, snomed_client)
    snomed_ms = (time.perf_counter() - snomed_started_at) * 1000

    concept_map_client = _get_concept_map_client(request)
    concept_map_ms = 0.0
    if concept_map_client.enabled:
        concept_map_started_at = time.perf_counter()
        enriched_entities = await _translate_entities(enriched_entities, concept_map_client)
        concept_map_ms = (time.perf_counter() - concept_map_started_at) * 1000
    total_ms = (time.perf_counter() - chunk_started_at) * 1000
    timings = ChunkProcessingTimings(
        asr_ms=asr_ms,
        ner_ms=ner_ms,
        snomed_ms=snomed_ms,
        concept_map_ms=concept_map_ms,
        total_ms=total_ms,
    )

    report_writer = _get_session_report_writer(request)
    if report_writer.enabled:
        report_writer.append_call(
            session_id=chunk.session_id,
            sequence=chunk.sequence,
            timestamp_ms=chunk.timestamp_ms,
            transcription_text=result.text,
            enriched_entities=enriched_entities,
            timings=timings,
            warning=warning,
        )
    else:
        log_transcription_call_to_console(
            transcription_text=result.text,
            enriched_entities=enriched_entities,
        )

    response[TRANSCRIBE_RESPONSE_KEY_ENTITIES] = [
        entity.to_dict() for entity in enriched_entities
    ]
    return response


@router.post("/finalize-session/{session_id}")
async def finalize_session(session_id: str, request: Request) -> dict[str, str]:
    writer = _get_session_report_writer(request)
    writer.flush_session(session_id)
    return {"session_id": session_id}


@router.post("/generate-report/{session_id}")
async def generate_report(session_id: str, request: Request) -> dict[str, str]:
    generator = _get_llm_report_generator(request)

    if not generator.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_LLM_DISABLED,
        )

    try:
        report = await generator.generate(session_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MSG_LLM_REPORT_NOT_FOUND.format(session_id=session_id),
        ) from exc
    except ConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return {"session_id": session_id, "report": report}


@router.post("/generate-fhir-report/{session_id}")
async def generate_fhir_report(
    session_id: str,
    request: Request,
    body: GenerateFhirReportRequest,
) -> dict[str, object]:
    generator = _get_fhir_report_generator(request)

    if not generator.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_FHIR_DISABLED,
        )

    fhir_report = await generator.generate(
        session_id,
        entities=body.entities,
    )

    return {"session_id": session_id, "fhir_report": fhir_report}
