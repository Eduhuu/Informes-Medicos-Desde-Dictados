from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedSessionEntity:
    """Enriched NER entity used to build FHIR resources."""

    index: int
    word: str
    entity_group: str
    pln_source_label: str
    score: float
    start: int
    end: int
    snomed_concept_id: str | None = None
    snomed_preferred_term: str | None = None
    snomed_preferred_lang: str | None = None
    snomed_fsn: str | None = None
    snomed_active: bool | None = None
    snomed_error: str | None = None
    snomed_no_match: bool = False

    @property
    def has_snomed_concept(self) -> bool:
        return self.snomed_concept_id is not None and not self.snomed_no_match
