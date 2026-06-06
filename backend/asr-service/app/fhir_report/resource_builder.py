import html
from typing import Union
from uuid import UUID, uuid4, uuid5

from fhir.resources.R4B.annotation import Annotation
from fhir.resources.R4B.bundle import BundleEntry
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.medicationstatement import MedicationStatement
from fhir.resources.R4B.meta import Meta
from fhir.resources.R4B.narrative import Narrative
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.procedure import Procedure
from fhir.resources.R4B.reference import Reference

from app.fhir_report.entity_mapper import resolve_fhir_resource_type
from app.fhir_report.models import ParsedSessionEntity
from shared.constants.FhirReportConstants import (
    FHIR_CONDITION_CLINICAL_ACTIVE,
    FHIR_CONDITION_CLINICAL_SYSTEM,
    FHIR_CONDITION_VERIFICATION_PROVISIONAL,
    FHIR_CONDITION_VERIFICATION_SYSTEM,
    FHIR_MEDICATION_STATEMENT_STATUS_ACTIVE,
    FHIR_NARRATIVE_STATUS_GENERATED,
    FHIR_NARRATIVE_XHTML_NS,
    FHIR_OBSERVATION_CATEGORY_EXAM,
    FHIR_OBSERVATION_CATEGORY_SYSTEM,
    FHIR_OBSERVATION_STATUS_FINAL,
    FHIR_PATIENT_ID_NAMESPACE,
    FHIR_PROCEDURE_STATUS_COMPLETED,
    FHIR_PROFILE_CONDITION,
    FHIR_PROFILE_MEDICATION_STATEMENT,
    FHIR_PROFILE_OBSERVATION,
    FHIR_PROFILE_PATIENT,
    FHIR_PROFILE_PROCEDURE,
    FHIR_RESOURCE_TYPE_CONDITION,
    FHIR_RESOURCE_TYPE_MEDICATION_STATEMENT,
    FHIR_RESOURCE_TYPE_PROCEDURE,
    FHIR_SESSION_PATIENT_IDENTIFIER_SYSTEM,
    FHIR_SNOMED_SYSTEM,
)

FhirClinicalResource = Union[Condition, MedicationStatement, Procedure, Observation]

_PATIENT_UUID_NAMESPACE = UUID(FHIR_PATIENT_ID_NAMESPACE)


def session_patient_id(session_id: str) -> str:
    """Deterministic lowercase UUID for the session Patient resource."""
    return str(uuid5(_PATIENT_UUID_NAMESPACE, session_id))


def build_patient_resource(session_id: str) -> Patient:
    patient_id = session_patient_id(session_id)
    summary = f"Paciente asociado a la sesión {session_id}"
    return Patient(
        id=patient_id,
        meta=Meta(profile=[FHIR_PROFILE_PATIENT]),
        text=_build_narrative(summary),
        identifier=[
            Identifier(
                system=FHIR_SESSION_PATIENT_IDENTIFIER_SYSTEM,
                value=session_id,
            )
        ],
    )


def build_entity_resource(
    entity: ParsedSessionEntity,
    *,
    patient_reference: str,
) -> FhirClinicalResource:
    resource_type = resolve_fhir_resource_type(entity)
    code = _build_codeable_concept(entity)

    if resource_type == FHIR_RESOURCE_TYPE_CONDITION:
        return _build_condition(entity, code, patient_reference)
    if resource_type == FHIR_RESOURCE_TYPE_MEDICATION_STATEMENT:
        return _build_medication_statement(entity, code, patient_reference)
    if resource_type == FHIR_RESOURCE_TYPE_PROCEDURE:
        return _build_procedure(entity, code, patient_reference)
    return _build_observation(entity, code, patient_reference)


def build_bundle_entry(resource: Union[Patient, FhirClinicalResource]) -> BundleEntry:
    resource_id = resource.id or str(uuid4())
    resource.id = resource_id
    return BundleEntry(
        fullUrl=f"urn:uuid:{resource_id}",
        resource=resource,
    )


def _build_narrative(summary: str) -> Narrative:
    escaped = html.escape(summary, quote=False)
    return Narrative(
        status=FHIR_NARRATIVE_STATUS_GENERATED,
        div=(
            f'<div xmlns="{FHIR_NARRATIVE_XHTML_NS}">'
            f"<p>{escaped}</p>"
            f"</div>"
        ),
    )


def _build_codeable_concept(entity: ParsedSessionEntity) -> CodeableConcept:
    codings: list[Coding] = []

    if entity.has_snomed_concept:
        codings.append(
            Coding(
                system=FHIR_SNOMED_SYSTEM,
                code=entity.snomed_concept_id,
                display=entity.snomed_preferred_term or entity.word.strip(),
            )
        )

    if entity.has_icd10_coding:
        codings.append(
            Coding(
                system=entity.icd10_system,
                code=entity.icd10_code,
                display=entity.icd10_display or None,
            )
        )

    if codings:
        return CodeableConcept(text=entity.word.strip(), coding=codings)

    return CodeableConcept(text=entity.word.strip())


def _build_detection_note(entity: ParsedSessionEntity) -> Annotation:
    snomed_status = "con concepto SNOMED"
    if entity.snomed_no_match:
        snomed_status = "sin concepto SNOMED"
    elif entity.snomed_error:
        snomed_status = f"error SNOMED: {entity.snomed_error}"
    return Annotation(
        text=(
            f"Detectado por NER ({entity.pln_source_label}, "
            f"etiqueta {entity.entity_group}, confianza {entity.score:.4f}, "
            f"posición {entity.start}-{entity.end}); {snomed_status}."
        )
    )


def _build_condition(
    entity: ParsedSessionEntity,
    code: CodeableConcept,
    patient_reference: str,
) -> Condition:
    label = code.text or entity.word
    return Condition(
        id=str(uuid4()),
        meta=Meta(profile=[FHIR_PROFILE_CONDITION]),
        text=_build_narrative(f"Condición detectada: {label}"),
        clinicalStatus=CodeableConcept(
            coding=[
                Coding(
                    system=FHIR_CONDITION_CLINICAL_SYSTEM,
                    code=FHIR_CONDITION_CLINICAL_ACTIVE,
                )
            ]
        ),
        verificationStatus=CodeableConcept(
            coding=[
                Coding(
                    system=FHIR_CONDITION_VERIFICATION_SYSTEM,
                    code=FHIR_CONDITION_VERIFICATION_PROVISIONAL,
                )
            ]
        ),
        code=code,
        subject=Reference(reference=patient_reference),
        note=[_build_detection_note(entity)],
    )


def _build_medication_statement(
    entity: ParsedSessionEntity,
    code: CodeableConcept,
    patient_reference: str,
) -> MedicationStatement:
    label = code.text or entity.word
    return MedicationStatement(
        id=str(uuid4()),
        meta=Meta(profile=[FHIR_PROFILE_MEDICATION_STATEMENT]),
        text=_build_narrative(f"Medicación mencionada: {label}"),
        status=FHIR_MEDICATION_STATEMENT_STATUS_ACTIVE,
        medicationCodeableConcept=code,
        subject=Reference(reference=patient_reference),
        note=[_build_detection_note(entity)],
    )


def _build_procedure(
    entity: ParsedSessionEntity,
    code: CodeableConcept,
    patient_reference: str,
) -> Procedure:
    label = code.text or entity.word
    return Procedure(
        id=str(uuid4()),
        meta=Meta(profile=[FHIR_PROFILE_PROCEDURE]),
        text=_build_narrative(f"Procedimiento o prueba: {label}"),
        status=FHIR_PROCEDURE_STATUS_COMPLETED,
        code=code,
        subject=Reference(reference=patient_reference),
        note=[_build_detection_note(entity)],
    )


def _build_observation(
    entity: ParsedSessionEntity,
    code: CodeableConcept,
    patient_reference: str,
) -> Observation:
    label = code.text or entity.word
    return Observation(
        id=str(uuid4()),
        meta=Meta(profile=[FHIR_PROFILE_OBSERVATION]),
        text=_build_narrative(f"Hallazgo clínico: {label}"),
        status=FHIR_OBSERVATION_STATUS_FINAL,
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system=FHIR_OBSERVATION_CATEGORY_SYSTEM,
                        code=FHIR_OBSERVATION_CATEGORY_EXAM,
                    )
                ]
            )
        ],
        code=code,
        subject=Reference(reference=patient_reference),
        note=[_build_detection_note(entity)],
    )
