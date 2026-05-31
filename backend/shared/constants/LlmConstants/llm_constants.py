"""Constants shared across LLM-related services."""

# Config file keys
CONFIG_KEY_LLM = "llm"
CONFIG_KEY_LLM_ENABLED = "enabled"
CONFIG_KEY_LLM_MODEL = "model"
CONFIG_KEY_LLM_SYSTEM_PROMPT = "system_prompt"
CONFIG_KEY_LLM_BASE_URL = "base_url"
CONFIG_KEY_LLM_TIMEOUT_SECONDS = "timeout_seconds"

# Default config values
DEFAULT_LLM_ENABLED = True
DEFAULT_LLM_MODEL = "llama3.1:8b"
DEFAULT_LLM_BASE_URL = "http://localhost:11434"
DEFAULT_LLM_TIMEOUT_SECONDS = 120

# Environment variable names
ENV_LLM_ENABLED = "LLM_ENABLED"
ENV_LLM_MODEL = "LLM_MODEL"
ENV_LLM_BASE_URL = "LLM_BASE_URL"
ENV_LLM_TIMEOUT_SECONDS = "LLM_TIMEOUT_SECONDS"
ENV_LLM_SYSTEM_PROMPT = "LLM_SYSTEM_PROMPT"

# Ollama API paths
OLLAMA_CHAT_PATH = "/api/chat"
OLLAMA_ROLE_SYSTEM = "system"
OLLAMA_ROLE_USER = "user"

# LLM report file naming
LLM_REPORT_FILENAME_PREFIX = "llm_report_"
LLM_REPORT_FILENAME_SUFFIX = ".txt"
