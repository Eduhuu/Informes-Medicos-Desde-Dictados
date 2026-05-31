"""Constants shared across ASR-related services."""

# Provider identifiers (config.yaml values)
PROVIDER_WHISPER = "fast-whisper"
PROVIDER_MOCK = "mock"

SUPPORTED_PROVIDERS = (PROVIDER_WHISPER, PROVIDER_MOCK)

# Default audio format (Whisper recommendation)
DEFAULT_SAMPLE_RATE_HZ = 16000
DEFAULT_CHANNELS = 1
DEFAULT_SAMPLE_WIDTH_BYTES = 2

# HTTP header names for chunk metadata
HEADER_SESSION_ID = "X-Session-Id"
HEADER_SEQUENCE = "X-Sequence"
HEADER_TIMESTAMP = "X-Timestamp"

# Config file keys
CONFIG_KEY_ASR = "asr"
CONFIG_KEY_PROVIDER = "provider"
CONFIG_KEY_MODEL = "model"
CONFIG_KEY_DEVICE = "device"
CONFIG_KEY_LANGUAGE = "language"
CONFIG_KEY_COMPUTE_TYPE = "compute_type"
CONFIG_KEY_PROMPT = "prompt"

# initial_prompt built from config prompt word list
INITIAL_PROMPT_WORD_SEPARATOR = ", "

ENV_ASR_PROMPT = "ASR_PROMPT"

# Default config values
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_DEVICE = "cpu"
DEFAULT_LANGUAGE = "es"
DEFAULT_COMPUTE_TYPE = "int8"
