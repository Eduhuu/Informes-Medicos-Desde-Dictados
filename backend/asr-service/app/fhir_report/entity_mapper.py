from app.constants.messages import REPORT_PLN_SOURCE_FARMACOS
from app.fhir_report.models import ParsedSessionEntity
from shared.constants.FhirReportConstants import (
    FHIR_ENTITY_GROUPS_CONDITION,
    FHIR_ENTITY_GROUPS_MEDICATION,
    FHIR_ENTITY_GROUPS_PROCEDURE,
    FHIR_RESOURCE_TYPE_CONDITION,
    FHIR_RESOURCE_TYPE_MEDICATION_STATEMENT,
    FHIR_RESOURCE_TYPE_OBSERVATION,
    FHIR_RESOURCE_TYPE_PROCEDURE,
    FHIR_SNOMED_FSN_TAG_DISORDER,
    FHIR_SNOMED_FSN_TAG_FINDING,
    FHIR_SNOMED_FSN_TAG_MEDICINAL_PRODUCT,
    FHIR_SNOMED_FSN_TAG_PROCEDURE,
)


def resolve_fhir_resource_type(entity: ParsedSessionEntity) -> str:
    """Choose FHIR resource type from NER label, PLN source and SNOMED FSN."""
    if entity.pln_source_label == REPORT_PLN_SOURCE_FARMACOS:
        return FHIR_RESOURCE_TYPE_MEDICATION_STATEMENT

    fsn = (entity.snomed_fsn or "").lower()
    if FHIR_SNOMED_FSN_TAG_MEDICINAL_PRODUCT in fsn:
        return FHIR_RESOURCE_TYPE_MEDICATION_STATEMENT
    if FHIR_SNOMED_FSN_TAG_PROCEDURE in fsn:
        return FHIR_RESOURCE_TYPE_PROCEDURE
    if FHIR_SNOMED_FSN_TAG_FINDING in fsn or FHIR_SNOMED_FSN_TAG_DISORDER in fsn:
        return FHIR_RESOURCE_TYPE_CONDITION

    group = entity.entity_group.upper()
    if group in FHIR_ENTITY_GROUPS_MEDICATION:
        return FHIR_RESOURCE_TYPE_MEDICATION_STATEMENT
    if group in FHIR_ENTITY_GROUPS_PROCEDURE:
        return FHIR_RESOURCE_TYPE_PROCEDURE
    if group in FHIR_ENTITY_GROUPS_CONDITION:
        return FHIR_RESOURCE_TYPE_CONDITION

    return FHIR_RESOURCE_TYPE_OBSERVATION
