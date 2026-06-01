"""Constants shared across FHIR report generation services."""

# Config file keys
CONFIG_KEY_FHIR_REPORT = "fhir_report"
CONFIG_KEY_FHIR_REPORT_ENABLED = "enabled"

# Default config values
DEFAULT_FHIR_REPORT_ENABLED = True

# Environment variable names
ENV_FHIR_REPORT_ENABLED = "FHIR_REPORT_ENABLED"

# FHIR report file naming (inside reports/<session_id>/)
FHIR_REPORT_FILENAME = "Fhir_Reporte.json"

# FHIR R4 Bundle stub literals
FHIR_RESOURCE_TYPE_BUNDLE = "Bundle"
FHIR_BUNDLE_TYPE_COLLECTION = "collection"
FHIR_BUNDLE_IDENTIFIER_SYSTEM = "urn:tfm:session-id"
