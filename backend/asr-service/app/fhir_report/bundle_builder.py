from datetime import datetime, timezone
from typing import Any

from shared.constants.FhirReportConstants import (
    FHIR_BUNDLE_IDENTIFIER_SYSTEM,
    FHIR_BUNDLE_TYPE_COLLECTION,
    FHIR_RESOURCE_TYPE_BUNDLE,
)


def build_stub_bundle(session_id: str) -> dict[str, Any]:
    """Build a minimal FHIR R4 Bundle placeholder for a session."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "resourceType": FHIR_RESOURCE_TYPE_BUNDLE,
        "type": FHIR_BUNDLE_TYPE_COLLECTION,
        "timestamp": timestamp,
        "identifier": {
            "system": FHIR_BUNDLE_IDENTIFIER_SYSTEM,
            "value": session_id,
        },
        "entry": [],
    }
