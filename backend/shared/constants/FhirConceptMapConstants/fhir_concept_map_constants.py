"""Constants shared across FHIR ConceptMap $translate and ValueSet $expand services."""

# Config file section key
CONFIG_KEY_FHIR_CONCEPT_MAP = "fhir_concept_map"

# Config file field keys
CONFIG_KEY_FHIR_CONCEPT_MAP_ENABLED = "enabled"
CONFIG_KEY_FHIR_CONCEPT_MAP_BASE_URL = "base_url"
CONFIG_KEY_FHIR_CONCEPT_MAP_URL = "concept_map_url"
CONFIG_KEY_FHIR_CONCEPT_MAP_FALLBACK_URL = "concept_map_fallback_url"
CONFIG_KEY_FHIR_CONCEPT_MAP_TIMEOUT_SECONDS = "timeout_seconds"
CONFIG_KEY_FHIR_CONCEPT_MAP_LANGUAGE = "language"
CONFIG_KEY_FHIR_VALUESET_EXPAND_URL = "value_set_expand_url"

# Default config values
DEFAULT_FHIR_CONCEPT_MAP_ENABLED = False
DEFAULT_FHIR_CONCEPT_MAP_BASE_URL = "http://localhost:8080/fhir"
DEFAULT_FHIR_CONCEPT_MAP_URL = "http://snomed.info/sct?fhir_cm=6011000124106"
DEFAULT_FHIR_CONCEPT_MAP_FALLBACK_URL = "http://snomed.info/sct?fhir_cm=447562003"
DEFAULT_FHIR_CONCEPT_MAP_TIMEOUT_SECONDS = 10.0
DEFAULT_FHIR_CONCEPT_MAP_LANGUAGE = "es"
DEFAULT_FHIR_VALUESET_EXPAND_URL = "http://snomed.info/sct/449081005?fhir_vs"

# Environment variable names
ENV_FHIR_CONCEPT_MAP_ENABLED = "FHIR_CONCEPT_MAP_ENABLED"
ENV_FHIR_CONCEPT_MAP_BASE_URL = "FHIR_CONCEPT_MAP_BASE_URL"
ENV_FHIR_CONCEPT_MAP_URL = "FHIR_CONCEPT_MAP_URL"
ENV_FHIR_CONCEPT_MAP_FALLBACK_URL = "FHIR_CONCEPT_MAP_FALLBACK_URL"
ENV_FHIR_CONCEPT_MAP_TIMEOUT_SECONDS = "FHIR_CONCEPT_MAP_TIMEOUT_SECONDS"
ENV_FHIR_CONCEPT_MAP_LANGUAGE = "FHIR_CONCEPT_MAP_LANGUAGE"
ENV_FHIR_VALUESET_EXPAND_URL = "FHIR_VALUESET_EXPAND_URL"

# HTTP header name for language negotiation
TRANSLATE_HEADER_ACCEPT_LANGUAGE = "Accept-Language"

# FHIR endpoint paths (relative to base_url)
FHIR_TRANSLATE_PATH = "ConceptMap/$translate"
FHIR_VALUESET_EXPAND_PATH = "ValueSet/$expand"

# FHIR $translate query parameter names
TRANSLATE_PARAM_CODE = "code"
TRANSLATE_PARAM_SYSTEM = "system"
TRANSLATE_PARAM_URL = "url"

# FHIR ValueSet/$expand query parameter names
VALUESET_PARAM_URL = "url"
VALUESET_PARAM_FILTER = "filter"

# SNOMED CT source system
FHIR_SNOMED_SYSTEM = "http://snomed.info/sct"

# Parameters resource keys (ConceptMap $translate response)
PARAM_RESOURCE_TYPE = "resourceType"
PARAM_RESOURCE_TYPE_PARAMETERS = "Parameters"
PARAM_KEY_PARAMETER = "parameter"
PARAM_KEY_NAME = "name"
PARAM_KEY_PART = "part"

# Top-level parameter names in the Parameters resource
PARAM_NAME_RESULT = "result"
PARAM_NAME_MATCH = "match"

# Part names inside each "match" parameter
PART_NAME_EQUIVALENCE = "equivalence"
PART_NAME_CONCEPT = "concept"

# Value keys inside parts
PART_VALUE_BOOLEAN = "valueBoolean"
PART_VALUE_CODE = "valueCode"
PART_VALUE_CODING = "valueCoding"

# Coding field keys
CODING_KEY_SYSTEM = "system"
CODING_KEY_CODE = "code"
CODING_KEY_DISPLAY = "display"

# ValueSet resource response keys (ValueSet/$expand response)
VALUESET_KEY_EXPANSION = "expansion"
VALUESET_KEY_CONTAINS = "contains"
VALUESET_KEY_SYSTEM = "system"
VALUESET_KEY_CODE = "code"
VALUESET_KEY_DISPLAY = "display"

# Translation source identifiers — indicate which lookup step produced the result
TRANSLATION_SOURCE_CM_PRIMARY = "concept_map_primary"
TRANSLATION_SOURCE_CM_FALLBACK = "concept_map_fallback"
TRANSLATION_SOURCE_VALUESET_EXPAND = "value_set_expand"
