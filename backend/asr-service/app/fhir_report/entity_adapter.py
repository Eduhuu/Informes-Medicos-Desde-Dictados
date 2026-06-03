from typing import Any

from app.fhir_report.models import ParsedSessionEntity
from app.services.pln_labels import pln_source_label


def entities_from_api_payload(entities: list[dict[str, Any]]) -> list[ParsedSessionEntity]:
    """Convert transcribe API entity dicts into ParsedSessionEntity instances."""
    parsed: list[ParsedSessionEntity] = []
    for index, raw in enumerate(entities, start=1):
        pln_source = str(raw.get("pln_source", ""))
        snomed_fields = _snomed_fields_from_api(raw.get("snomed") or {})
        parsed.append(
            ParsedSessionEntity(
                index=index,
                word=str(raw.get("word", "")),
                entity_group=str(raw.get("entity_group", "")),
                pln_source_label=pln_source_label(pln_source),
                score=float(raw.get("score", 0)),
                start=int(raw.get("start", 0)),
                end=int(raw.get("end", 0)),
                **snomed_fields,
            ),
        )
    return parsed


def _snomed_fields_from_api(snomed: dict[str, Any]) -> dict[str, Any]:
    error = snomed.get("error")
    if error:
        return {"snomed_error": str(error)}

    items = snomed.get("items") or []
    if not items:
        return {"snomed_no_match": True}

    concept = items[0]
    pt = concept.get("pt") or {}
    fsn = concept.get("fsn") or {}
    return {
        "snomed_concept_id": str(concept.get("conceptId", "")) or None,
        "snomed_preferred_term": str(pt.get("term", "")) or None,
        "snomed_preferred_lang": str(pt.get("lang", "")) or None,
        "snomed_fsn": str(fsn.get("term", "")) or None,
        "snomed_active": bool(concept.get("active")) if "active" in concept else None,
    }
