import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.constants.AsrConstants import (
    CONFIG_KEY_ASR,
    CONFIG_KEY_COMPUTE_TYPE,
    CONFIG_KEY_DEVICE,
    CONFIG_KEY_LANGUAGE,
    CONFIG_KEY_MODEL,
    CONFIG_KEY_PROVIDER,
    DEFAULT_COMPUTE_TYPE,
    DEFAULT_DEVICE,
    DEFAULT_LANGUAGE,
    DEFAULT_WHISPER_MODEL,
    PROVIDER_MOCK,
)

from shared.constants.PlnConstants import (
    CONFIG_KEY_PLN,
    CONFIG_KEY_TASK,
    CONFIG_KEY_MODEL,
    CONFIG_KEY_AGGREGATION_STRATEGY,
    DEFAULT_TASK,
    DEFAULT_TASK_MODEL,
    DEFAULT_TASK_AGGREGATION_STRATEGY,
)

@dataclass(frozen=True)
class AsrSettings:
    provider: str
    model: str
    device: str
    language: str
    compute_type: str

@dataclass(frozen=True)
class PlnSettings:
    task: str
    model: str
    aggregation_strategy: str

@dataclass(frozen=True)
class Settings:
    asr: AsrSettings
    pln: PlnSettings

def _default_config_path() -> Path:
    env_path = os.getenv("ASR_CONFIG_PATH")
    if env_path:
        return Path(env_path)

    return Path(__file__).resolve().parents[2] / "config.yaml"


def load_settings(config_path: Path | None = None) -> Settings:
    path = config_path or _default_config_path()

    if not path.exists():
        return Settings(
            asr=AsrSettings(
            provider=os.getenv("ASR_PROVIDER", PROVIDER_MOCK),
            model=os.getenv("ASR_MODEL", DEFAULT_WHISPER_MODEL),
                device=os.getenv("ASR_DEVICE", DEFAULT_DEVICE),
                language=os.getenv("ASR_LANGUAGE", DEFAULT_LANGUAGE),
                compute_type=os.getenv("ASR_COMPUTE_TYPE", DEFAULT_COMPUTE_TYPE),
            ),
            pln=PlnSettings(
                task=os.getenv("PLN_TASK", "text-classification"),
                model=os.getenv("PLN_MODEL", "bert-base-uncased"),
                aggregation_strategy=os.getenv("PLN_AGGREGATION_STRATEGY", "mean"),
            ),
        )
    with path.open(encoding="utf-8") as config_file:
        raw: dict[str, Any] = yaml.safe_load(config_file) or {}
    asr_section = raw.get(CONFIG_KEY_ASR, {})
    pln_section = raw.get(CONFIG_KEY_PLN, {})
    return Settings(
        asr=AsrSettings(
            provider=str(asr_section.get(CONFIG_KEY_PROVIDER, os.getenv("ASR_PROVIDER", PROVIDER_MOCK))),
            model=str(asr_section.get(CONFIG_KEY_MODEL, DEFAULT_WHISPER_MODEL)),
            device=str(asr_section.get(CONFIG_KEY_DEVICE, DEFAULT_DEVICE)),
            language=str(asr_section.get(CONFIG_KEY_LANGUAGE, DEFAULT_LANGUAGE)),
            compute_type=str(asr_section.get(CONFIG_KEY_COMPUTE_TYPE, DEFAULT_COMPUTE_TYPE)),
        ),
        pln=PlnSettings(
            task=str(pln_section.get(CONFIG_KEY_TASK, DEFAULT_TASK)),
            model=str(pln_section.get(CONFIG_KEY_MODEL, DEFAULT_TASK_MODEL)),
            aggregation_strategy=str(pln_section.get(CONFIG_KEY_AGGREGATION_STRATEGY, DEFAULT_TASK_AGGREGATION_STRATEGY)),
        ),
    )
