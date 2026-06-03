"""Constants shared across PLN-related services."""
CONFIG_KEY_PLN = "pln"
CONFIG_KEY_PLN_MEDICAL = "pln_medical"
CONFIG_KEY_PLN_FARMACOS = "pln_farmacos"

# PLN model identifiers (config.yaml values)
PLN_MODEL_RIGONSALLAUKA = "rigonsallauka/spanish_medical_ner"
PLN_MODEL_PHARMACONER = "PlanTL-GOB-ES/bsc-bio-ehr-es-pharmaconer"
PLN_MODEL_MEDICAL = "PlanTL-GOB-ES/bsc-bio-ehr-es"

SUPPORTED_PLN_MODELS = frozenset({
    PLN_MODEL_RIGONSALLAUKA,
    PLN_MODEL_PHARMACONER,
    PLN_MODEL_MEDICAL,
})

# Internal entity source identifiers
PLN_SOURCE_MEDICAL = "pln_medical"
PLN_SOURCE_FARMACOS = "pln_farmacos"

# Config file keys
CONFIG_KEY_TASK = "task"
CONFIG_KEY_MODEL = "model"
CONFIG_KEY_AGGREGATION_STRATEGY = "aggregation_strategy"

# Default config values (medical PLN)
DEFAULT_TASK = "ner"
DEFAULT_TASK_MODEL = PLN_MODEL_RIGONSALLAUKA
DEFAULT_TASK_AGGREGATION_STRATEGY = "max"

# Default config values (farmacos PLN)
DEFAULT_FARMACOS_TASK = "token-classification"
DEFAULT_FARMACOS_MODEL = PLN_MODEL_PHARMACONER
DEFAULT_FARMACOS_AGGREGATION_STRATEGY = "simple"

# Thread pool for parallel PLN execution
PLN_EXECUTOR_MAX_WORKERS = 2

# NER entity dict field keys (HuggingFace pipeline output)
NER_KEY_ENTITY_GROUP = "entity_group"
NER_KEY_WORD = "word"
NER_KEY_START = "start"
NER_KEY_END = "end"
NER_KEY_SCORE = "score"

# Maximum character gap between two consecutive entities to still consider them
# part of the same multi-token concept (e.g. "diabetes mellitus tipo 2")
NER_GROUP_SPACE_TOLERANCE = 1
