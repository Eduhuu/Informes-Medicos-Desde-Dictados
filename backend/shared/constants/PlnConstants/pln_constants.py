"""Constants shared across PLN-related services."""
CONFIG_KEY_PLN = "pln"

# PNL model identifiers (config.yaml values)
PLN_MODEL_RIGONSALLAUKA = "rigonsallauka/spanish_medical_ner"


# Config file keys
CONFIG_KEY_TASK = "task"
CONFIG_KEY_MODEL = "model"
CONFIG_KEY_AGGREGATION_STRATEGY = "aggregation_strategy"

# Default config values
DEFAULT_TASK = "ner"
DEFAULT_TASK_MODEL = PLN_MODEL_RIGONSALLAUKA
DEFAULT_TASK_AGGREGATION_STRATEGY = "max"
