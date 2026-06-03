from datetime import datetime, timezone

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.identifier import Identifier

from app.fhir_report.models import ParsedSessionEntity
from app.fhir_report.resource_builder import (
    build_bundle_entry,
    build_entity_resource,
    build_patient_resource,
    session_patient_id,
)
from shared.constants.FhirReportConstants import (
    FHIR_BUNDLE_IDENTIFIER_SYSTEM,
    FHIR_BUNDLE_TYPE_COLLECTION,
)


def build_bundle_from_entities(
    session_id: str,
    entities: list[ParsedSessionEntity],
) -> Bundle:
    """Build a FHIR R4B Bundle populated with resources from detected entities."""
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    patient_reference = f"Patient/{session_patient_id(session_id)}"

    entries = [build_bundle_entry(build_patient_resource(session_id))]

    for entity in entities:
        resource = build_entity_resource(
            entity,
            patient_reference=patient_reference,
        )
        entries.append(build_bundle_entry(resource))

    return Bundle(
        type=FHIR_BUNDLE_TYPE_COLLECTION,
        timestamp=timestamp,
        identifier=Identifier(
            system=FHIR_BUNDLE_IDENTIFIER_SYSTEM,
            value=session_id,
        ),
        entry=entries,
    )
