import json
from pathlib import Path
from typing import Any

from app.config.settings import FhirReportSettings
from app.constants.messages import MSG_FHIR_REPORT_NOT_FOUND
from app.fhir_report.bundle_builder import build_stub_bundle
from app.services.report_paths import (
    control_report_path,
    ensure_session_reports_dir,
    fhir_report_path,
)


class FhirReportGenerator:
    """Reads a session report and generates a FHIR Bundle JSON report."""

    def __init__(self, settings: FhirReportSettings, reports_dir: Path) -> None:
        self._settings = settings
        self._reports_dir = reports_dir

    @property
    def enabled(self) -> bool:
        return self._settings.enabled

    async def generate(self, session_id: str) -> dict[str, Any]:
        session_report_path = control_report_path(self._reports_dir, session_id)
        if not session_report_path.exists():
            raise FileNotFoundError(
                MSG_FHIR_REPORT_NOT_FOUND.format(session_id=session_id),
            )

        bundle = build_stub_bundle(session_id)

        ensure_session_reports_dir(self._reports_dir, session_id)
        output_path = fhir_report_path(self._reports_dir, session_id)
        output_path.write_text(
            json.dumps(bundle, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return bundle
