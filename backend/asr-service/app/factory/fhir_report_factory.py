from pathlib import Path

from app.config.settings import FhirReportSettings
from app.services.fhir_report_generator import FhirReportGenerator


class FhirReportFactory:
    """Builds the FHIR report generator from configuration."""

    @staticmethod
    def create(settings: FhirReportSettings, reports_dir: Path) -> FhirReportGenerator:
        return FhirReportGenerator(settings, reports_dir)
