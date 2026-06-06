from typing import Any

from app.fhir_report.models import ParsedSessionEntity
from app.services.pln_labels import pln_source_label


def entities_from_api_payload(entities: list[dict[str, Any]]) -> list[ParsedSessionEntity]:
    """Convert transcribe API entity dicts into ParsedSessionEntity instances."""
    parsed: list[ParsedSessionEntity] = []
    for index, raw in enumerate(entities, start=1):
        pln_source = str(raw.get("pln_source", ""))
        snomed_fields = _snomed_fields_from_api(raw.get("snomed") or {})
        icd10_fields = _icd10_fields_from_api(raw.get("concept_map") or {})
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
                **icd10_fields,
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


def _icd10_fields_from_api(concept_map: dict[str, Any]) -> dict[str, Any]:
    if not concept_map.get("result"):
        return {}

    matches: list[dict[str, Any]] = concept_map.get("matches") or []
    if not matches:
        return {}

    first = matches[0]
    code = str(first.get("code", "")) or None
    system = str(first.get("system", "")) or None
    if not code or not system:
        return {}

    return {
        "icd10_code": code,
        "icd10_display": str(first.get("display", "")) or None,
        "icd10_system": system,
        "icd10_source": str(concept_map.get("source", "")) or None,
    }
