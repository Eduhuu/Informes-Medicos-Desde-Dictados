import re
from pathlib import Path

from shared.constants.FhirReportConstants import FHIR_REPORT_FILENAME
from shared.constants.LlmConstants import LLM_REPORT_FILENAME
from shared.constants.ReportConstants import CONTROL_REPORT_FILENAME

_SAFE_SESSION_ID_PATTERN = re.compile(r"[^\w\-]+")


def sanitize_session_id(session_id: str) -> str:
    return _SAFE_SESSION_ID_PATTERN.sub("_", session_id).strip("_") or "default"


def session_reports_dir(reports_dir: Path, session_id: str) -> Path:
    return reports_dir / sanitize_session_id(session_id)


def ensure_session_reports_dir(reports_dir: Path, session_id: str) -> Path:
    directory = session_reports_dir(reports_dir, session_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def control_report_path(reports_dir: Path, session_id: str) -> Path:
    return session_reports_dir(reports_dir, session_id) / CONTROL_REPORT_FILENAME


def llm_report_path(reports_dir: Path, session_id: str) -> Path:
    return session_reports_dir(reports_dir, session_id) / LLM_REPORT_FILENAME


def fhir_report_path(reports_dir: Path, session_id: str) -> Path:
    return session_reports_dir(reports_dir, session_id) / FHIR_REPORT_FILENAME
