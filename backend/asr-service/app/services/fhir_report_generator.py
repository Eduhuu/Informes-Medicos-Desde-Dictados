import json
from pathlib import Path
from typing import Any

from app.config.settings import FhirReportSettings
from app.fhir_report.bundle_builder import build_bundle_from_entities
from app.fhir_report.entity_adapter import entities_from_api_payload
from app.services.report_paths import (
    ensure_session_reports_dir,
    fhir_report_path,
)


class FhirReportGenerator:
    """Generates a FHIR Bundle JSON report from enriched entities."""

    def __init__(self, settings: FhirReportSettings, reports_dir: Path) -> None:
        self._settings = settings
        self._reports_dir = reports_dir

    @property
    def enabled(self) -> bool:
        return self._settings.enabled

    async def generate(
        self,
        session_id: str,
        *,
        entities: list[dict[str, Any]],
    ) -> dict[str, Any]:
        parsed_entities = entities_from_api_payload(entities)
        bundle = build_bundle_from_entities(session_id, parsed_entities)

        payload = bundle.model_dump(mode="json", exclude_none=True)

        ensure_session_reports_dir(self._reports_dir, session_id)
        output_path = fhir_report_path(self._reports_dir, session_id)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return payload
