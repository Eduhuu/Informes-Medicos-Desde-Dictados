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
    CONFIG_KEY_AGGREGATION_STRATEGY,
    CONFIG_KEY_MODEL,
    CONFIG_KEY_PLN,
    CONFIG_KEY_PLN_FARMACOS,
    CONFIG_KEY_PLN_MEDICAL,
    CONFIG_KEY_TASK,
    DEFAULT_FARMACOS_AGGREGATION_STRATEGY,
    DEFAULT_FARMACOS_MODEL,
    DEFAULT_FARMACOS_TASK,
    DEFAULT_TASK,
    DEFAULT_TASK_AGGREGATION_STRATEGY,
    DEFAULT_TASK_MODEL,
)

from shared.constants.ReportConstants import (
    CONFIG_KEY_REPORTS,
    CONFIG_KEY_REPORTS_DIR,
    CONFIG_KEY_REPORTS_ENABLED,
    DEFAULT_REPORTS_DIR_NAME,
    DEFAULT_REPORTS_ENABLED,
    ENV_REPORTS_DIR,
    ENV_REPORTS_ENABLED,
)

from shared.constants.SnomedConstants import (
    CONFIG_KEY_SNOMED,
    CONFIG_KEY_ACTIVE,
    CONFIG_KEY_BASE_URL,
    CONFIG_KEY_BRANCH,
    CONFIG_KEY_ENABLED,
    CONFIG_KEY_LIMIT,
    CONFIG_KEY_PREFERRED_LANGUAGE,
    CONFIG_KEY_PROVIDER,
    CONFIG_KEY_TIMEOUT_SECONDS,
    DEFAULT_SNOMED_ACTIVE,
    DEFAULT_SNOMED_BASE_URL,
    DEFAULT_SNOMED_BRANCH,
    DEFAULT_SNOMED_ENABLED,
    DEFAULT_SNOMED_LIMIT,
    DEFAULT_SNOMED_PREFERRED_LANGUAGE,
    DEFAULT_SNOMED_PROVIDER,
    DEFAULT_SNOMED_TIMEOUT_SECONDS,
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
class ReportSettings:
    enabled: bool
    directory: Path


@dataclass(frozen=True)
class SnomedSettings:
    enabled: bool
    provider: str
    base_url: str
    branch: str
    limit: int
    active: bool
    preferred_language: str
    timeout_seconds: float


@dataclass(frozen=True)
class Settings:
    asr: AsrSettings
    pln_medical: PlnSettings
    pln_farmacos: PlnSettings
    snomed: SnomedSettings
    reports: ReportSettings


def _build_pln_settings(
    section: dict[str, Any],
    *,
    default_task: str,
    default_model: str,
    default_aggregation_strategy: str,
) -> PlnSettings:
    return PlnSettings(
        task=str(section.get(CONFIG_KEY_TASK, default_task)),
        model=str(section.get(CONFIG_KEY_MODEL, default_model)),
        aggregation_strategy=str(
            section.get(
                CONFIG_KEY_AGGREGATION_STRATEGY,
                default_aggregation_strategy,
            ),
        ),
    )


def _default_pln_medical_from_env() -> PlnSettings:
    return PlnSettings(
        task=os.getenv("PLN_MEDICAL_TASK", os.getenv("PLN_TASK", DEFAULT_TASK)),
        model=os.getenv(
            "PLN_MEDICAL_MODEL",
            os.getenv("PLN_MODEL", DEFAULT_TASK_MODEL),
        ),
        aggregation_strategy=os.getenv(
            "PLN_MEDICAL_AGGREGATION_STRATEGY",
            os.getenv("PLN_AGGREGATION_STRATEGY", DEFAULT_TASK_AGGREGATION_STRATEGY),
        ),
    )


def _default_pln_farmacos_from_env() -> PlnSettings:
    return PlnSettings(
        task=os.getenv("PLN_FARMACOS_TASK", DEFAULT_FARMACOS_TASK),
        model=os.getenv("PLN_FARMACOS_MODEL", DEFAULT_FARMACOS_MODEL),
        aggregation_strategy=os.getenv(
            "PLN_FARMACOS_AGGREGATION_STRATEGY",
            DEFAULT_FARMACOS_AGGREGATION_STRATEGY,
        ),
    )

def _default_reports_directory() -> Path:
    return Path(__file__).resolve().parents[2] / DEFAULT_REPORTS_DIR_NAME


def _build_report_settings(reports_section: dict[str, Any]) -> ReportSettings:
    raw_dir = reports_section.get(CONFIG_KEY_REPORTS_DIR)
    directory = (
        Path(str(raw_dir))
        if raw_dir
        else _default_reports_directory()
    )
    return ReportSettings(
        enabled=_parse_bool(
            reports_section.get(CONFIG_KEY_REPORTS_ENABLED),
            DEFAULT_REPORTS_ENABLED,
        ),
        directory=directory,
    )


def _default_report_settings_from_env() -> ReportSettings:
    env_dir = os.getenv(ENV_REPORTS_DIR)
    return ReportSettings(
        enabled=_parse_bool(
            os.getenv(ENV_REPORTS_ENABLED),
            DEFAULT_REPORTS_ENABLED,
        ),
        directory=Path(env_dir) if env_dir else _default_reports_directory(),
    )


def _default_config_path() -> Path:
    env_path = os.getenv("ASR_CONFIG_PATH")
    if env_path:
        return Path(env_path)

    return Path(__file__).resolve().parents[2] / "config.yaml"


def _parse_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes", "on")


def _build_snomed_settings(
    snomed_section: dict[str, Any],
) -> SnomedSettings:
    return SnomedSettings(
        enabled=_parse_bool(
            snomed_section.get(CONFIG_KEY_ENABLED),
            DEFAULT_SNOMED_ENABLED,
        ),
        provider=str(
            snomed_section.get(CONFIG_KEY_PROVIDER, DEFAULT_SNOMED_PROVIDER),
        ),
        base_url=str(
            snomed_section.get(CONFIG_KEY_BASE_URL, DEFAULT_SNOMED_BASE_URL),
        ),
        branch=str(
            snomed_section.get(CONFIG_KEY_BRANCH, DEFAULT_SNOMED_BRANCH),
        ),
        limit=int(snomed_section.get(CONFIG_KEY_LIMIT, DEFAULT_SNOMED_LIMIT)),
        active=_parse_bool(
            snomed_section.get(CONFIG_KEY_ACTIVE),
            DEFAULT_SNOMED_ACTIVE,
        ),
        preferred_language=str(
            snomed_section.get(
                CONFIG_KEY_PREFERRED_LANGUAGE,
                DEFAULT_SNOMED_PREFERRED_LANGUAGE,
            ),
        ),
        timeout_seconds=float(
            snomed_section.get(
                CONFIG_KEY_TIMEOUT_SECONDS,
                DEFAULT_SNOMED_TIMEOUT_SECONDS,
            ),
        ),
    )


def _default_snomed_settings_from_env() -> SnomedSettings:
    return SnomedSettings(
        enabled=_parse_bool(
            os.getenv("SNOMED_ENABLED"),
            DEFAULT_SNOMED_ENABLED,
        ),
        provider=os.getenv("SNOMED_PROVIDER", DEFAULT_SNOMED_PROVIDER),
        base_url=os.getenv("SNOMED_BASE_URL", DEFAULT_SNOMED_BASE_URL),
        branch=os.getenv("SNOMED_BRANCH", DEFAULT_SNOMED_BRANCH),
        limit=int(os.getenv("SNOMED_LIMIT", str(DEFAULT_SNOMED_LIMIT))),
        active=_parse_bool(
            os.getenv("SNOMED_ACTIVE"),
            DEFAULT_SNOMED_ACTIVE,
        ),
        preferred_language=os.getenv(
            "SNOMED_PREFERRED_LANGUAGE",
            DEFAULT_SNOMED_PREFERRED_LANGUAGE,
        ),
        timeout_seconds=float(
            os.getenv(
                "SNOMED_TIMEOUT_SECONDS",
                str(DEFAULT_SNOMED_TIMEOUT_SECONDS),
            ),
        ),
    )


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
            pln_medical=_default_pln_medical_from_env(),
            pln_farmacos=_default_pln_farmacos_from_env(),
            snomed=_default_snomed_settings_from_env(),
            reports=_default_report_settings_from_env(),
        )
    with path.open(encoding="utf-8") as config_file:
        raw: dict[str, Any] = yaml.safe_load(config_file) or {}
    asr_section = raw.get(CONFIG_KEY_ASR, {})
    pln_medical_section = raw.get(CONFIG_KEY_PLN_MEDICAL, {})
    if not pln_medical_section:
        pln_medical_section = raw.get(CONFIG_KEY_PLN, {})
    pln_farmacos_section = raw.get(CONFIG_KEY_PLN_FARMACOS, {})
    snomed_section = raw.get(CONFIG_KEY_SNOMED, {})
    reports_section = raw.get(CONFIG_KEY_REPORTS, {})
    return Settings(
        asr=AsrSettings(
            provider=str(asr_section.get(CONFIG_KEY_PROVIDER, os.getenv("ASR_PROVIDER", PROVIDER_MOCK))),
            model=str(asr_section.get(CONFIG_KEY_MODEL, DEFAULT_WHISPER_MODEL)),
            device=str(asr_section.get(CONFIG_KEY_DEVICE, DEFAULT_DEVICE)),
            language=str(asr_section.get(CONFIG_KEY_LANGUAGE, DEFAULT_LANGUAGE)),
            compute_type=str(asr_section.get(CONFIG_KEY_COMPUTE_TYPE, DEFAULT_COMPUTE_TYPE)),
        ),
        pln_medical=_build_pln_settings(
            pln_medical_section,
            default_task=DEFAULT_TASK,
            default_model=DEFAULT_TASK_MODEL,
            default_aggregation_strategy=DEFAULT_TASK_AGGREGATION_STRATEGY,
        ),
        pln_farmacos=_build_pln_settings(
            pln_farmacos_section,
            default_task=DEFAULT_FARMACOS_TASK,
            default_model=DEFAULT_FARMACOS_MODEL,
            default_aggregation_strategy=DEFAULT_FARMACOS_AGGREGATION_STRATEGY,
        ),
        snomed=_build_snomed_settings(snomed_section),
        reports=_build_report_settings(reports_section),
    )
