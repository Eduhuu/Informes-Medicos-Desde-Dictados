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

# API contract (generate-fhir-report request body)
FHIR_REQUEST_BODY_KEY_ENTITIES = "entities"

# FHIR R4 Bundle literals
FHIR_RESOURCE_TYPE_BUNDLE = "Bundle"
FHIR_BUNDLE_TYPE_COLLECTION = "collection"
FHIR_BUNDLE_IDENTIFIER_SYSTEM = "urn:tfm:session-id"

# FHIR resource types
FHIR_RESOURCE_TYPE_PATIENT = "Patient"
FHIR_RESOURCE_TYPE_CONDITION = "Condition"
FHIR_RESOURCE_TYPE_MEDICATION_STATEMENT = "MedicationStatement"
FHIR_RESOURCE_TYPE_PROCEDURE = "Procedure"
FHIR_RESOURCE_TYPE_OBSERVATION = "Observation"

# FHIR terminology systems
FHIR_SNOMED_SYSTEM = "http://snomed.info/sct"
FHIR_CONDITION_CLINICAL_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-clinical"
FHIR_CONDITION_VERIFICATION_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
FHIR_OBSERVATION_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/observation-category"
FHIR_MEDICATION_STATEMENT_STATUS_SYSTEM = (
    "http://hl7.org/fhir/CodeSystem/medication-statement-status"
)
FHIR_PROCEDURE_STATUS_SYSTEM = "http://hl7.org/fhir/CodeSystem/event-status"
FHIR_OBSERVATION_STATUS_SYSTEM = "http://hl7.org/fhir/CodeSystem/observation-status"
FHIR_SESSION_PATIENT_IDENTIFIER_SYSTEM = "urn:tfm:session-patient"

# FHIR coded values
FHIR_CONDITION_CLINICAL_ACTIVE = "active"
FHIR_CONDITION_VERIFICATION_PROVISIONAL = "provisional"
FHIR_MEDICATION_STATEMENT_STATUS_ACTIVE = "active"
FHIR_PROCEDURE_STATUS_COMPLETED = "completed"
FHIR_OBSERVATION_STATUS_FINAL = "final"
FHIR_OBSERVATION_CATEGORY_EXAM = "exam"

# Narrative (dom-6 best practice)
FHIR_NARRATIVE_STATUS_GENERATED = "generated"
FHIR_NARRATIVE_XHTML_NS = "http://www.w3.org/1999/xhtml"

# Stable UUID namespace for session-scoped Patient ids (RFC 4122 URL namespace)
FHIR_PATIENT_ID_NAMESPACE = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"

# R4 structure definition canonical URLs (meta.profile)
FHIR_PROFILE_PATIENT = "http://hl7.org/fhir/StructureDefinition/Patient"
FHIR_PROFILE_CONDITION = "http://hl7.org/fhir/StructureDefinition/Condition"
FHIR_PROFILE_MEDICATION_STATEMENT = (
    "http://hl7.org/fhir/StructureDefinition/MedicationStatement"
)
FHIR_PROFILE_PROCEDURE = "http://hl7.org/fhir/StructureDefinition/Procedure"
FHIR_PROFILE_OBSERVATION = "http://hl7.org/fhir/StructureDefinition/Observation"

# SNOMED FSN semantic tag hints (English, from Snowstorm)
FHIR_SNOMED_FSN_TAG_MEDICINAL_PRODUCT = "(medicinal product)"
FHIR_SNOMED_FSN_TAG_PROCEDURE = "(procedure)"
FHIR_SNOMED_FSN_TAG_FINDING = "(finding)"
FHIR_SNOMED_FSN_TAG_DISORDER = "(disorder)"

# NER entity_group → FHIR resource type (fallback when SNOMED FSN is ambiguous)
FHIR_ENTITY_GROUPS_MEDICATION = frozenset({
    "NORMALIZABLES",
    "CHEM",
    "DRUG",
    "MEDICATION",
    "FARMACO",
})
FHIR_ENTITY_GROUPS_CONDITION = frozenset({
    "PROBLEM",
    "SYMPTOM",
    "DISEASE",
    "DISORDER",
})
FHIR_ENTITY_GROUPS_PROCEDURE = frozenset({
    "TEST",
    "PROCEDURE",
    "PROC",
})
