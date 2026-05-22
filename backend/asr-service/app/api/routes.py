from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.constants.messages import (
    MSG_HEALTH_OK,
    MSG_HEALTH_UNAVAILABLE,
    MSG_INVALID_SEQUENCE,
    MSG_MISSING_AUDIO,
    MSG_SERVICE_READY,
    MSG_TRANSCRIPTION_EMPTY,
)
from app.models.audio_chunk import AudioChunk
from app.providers.base import ASRProvider
from shared.constants.AsrConstants import (
    DEFAULT_CHANNELS,
    DEFAULT_SAMPLE_RATE_HZ,
    DEFAULT_SAMPLE_WIDTH_BYTES,
    HEADER_SEQUENCE,
    HEADER_SESSION_ID,
    HEADER_TIMESTAMP,
)

router = APIRouter()


def _get_provider(request: Request) -> ASRProvider:
    provider = getattr(request.app.state, "asr_provider", None)
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MSG_HEALTH_UNAVAILABLE,
        )
    return provider


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

    provider = _get_provider(request)
    result = provider.transcribe(chunk)
    response = result.to_dict()
    
    if not result.text:
        response["warning"] = MSG_TRANSCRIPTION_EMPTY
    print(result.text)
    return response
