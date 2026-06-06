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
    icd10_code: str | None = None
    icd10_display: str | None = None
    icd10_system: str | None = None
    icd10_source: str | None = None

    @property
    def has_snomed_concept(self) -> bool:
        return self.snomed_concept_id is not None and not self.snomed_no_match

    @property
    def has_icd10_coding(self) -> bool:
        return self.icd10_code is not None and self.icd10_system is not None
