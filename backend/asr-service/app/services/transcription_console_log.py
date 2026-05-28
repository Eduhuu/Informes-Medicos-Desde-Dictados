from dataclasses import asdict

from app.constants.messages import (
    LOG_NER_ENTITY,
    LOG_SNOMED_ERROR,
    LOG_SNOMED_NOT_FOUND,
    LOG_SNOMED_RESULT,
    LOG_TRANSCRIPTION,
)
from app.models.snomed import EnrichedEntity
from app.services.pln_labels import pln_source_label


def log_transcription_call_to_console(
    *,
    transcription_text: str,
    enriched_entities: list[EnrichedEntity],
) -> None:
    """Mirror legacy stdout logging when session reports are disabled."""
    if not transcription_text.strip():
        return

    print(LOG_TRANSCRIPTION.format(text=transcription_text))

    for entity in enriched_entities:
        print(
            LOG_NER_ENTITY.format(
                word=entity.word,
                pln_source_label=pln_source_label(entity.pln_source),
            ),
        )
        snomed = entity.snomed

        if snomed.error:
            print(
                LOG_SNOMED_ERROR.format(word=entity.word, error=snomed.error),
            )
            continue

        if snomed.total == 0 or not snomed.items:
            print(LOG_SNOMED_NOT_FOUND.format(word=entity.word))
            continue

        print(LOG_SNOMED_RESULT.format(snomed=asdict(snomed.items[0])))
