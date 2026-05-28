from typing import Any

from app.models.snomed import EnrichedEntity
from app.snomed.base import SnomedClient


def normalize_ner_entity(ner_entity: dict[str, Any]) -> dict[str, Any]:
    """Convert HuggingFace NER output to JSON-serializable Python types."""
    return {
        "word": str(ner_entity["word"]),
        "score": float(ner_entity["score"]),
        "entity_group": str(ner_entity["entity_group"]),
        "start": int(ner_entity["start"]),
        "end": int(ner_entity["end"]),
        "pln_source": str(ner_entity["pln_source"]),
    }


def enrich_entities(
    ner_entities: list[dict[str, Any]],
    snomed_client: SnomedClient,
) -> list[EnrichedEntity]:
    """Attach SNOMED concept search results to each NER entity."""
    enriched: list[EnrichedEntity] = []
    for ner_entity in ner_entities:
        normalized = normalize_ner_entity(ner_entity)
        snomed_result = snomed_client.search_concepts(normalized["word"])
        enriched.append(
            EnrichedEntity.from_ner_entity(normalized, snomed_result),
        )
    return enriched
