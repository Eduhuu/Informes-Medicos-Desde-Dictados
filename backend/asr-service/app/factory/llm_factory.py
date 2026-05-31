from pathlib import Path

from app.config.settings import LlmSettings
from app.services.llm_report_generator import LlmReportGenerator


class LlmFactory:
    """Builds the LLM report generator from configuration."""

    @staticmethod
    def create(settings: LlmSettings, reports_dir: Path) -> LlmReportGenerator:
        return LlmReportGenerator(settings, reports_dir)
