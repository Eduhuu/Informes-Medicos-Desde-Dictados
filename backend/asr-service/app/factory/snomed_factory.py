import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.config.settings import SnomedSettings, load_settings
from app.constants.messages import MSG_INVALID_SNOMED_PROVIDER
from app.snomed.base import SnomedClient
from shared.constants.SnomedConstants import PROVIDER_MOCK, PROVIDER_SNOWSTORM


class SnomedFactory:
    """Builds the active SNOMED client from configuration."""

    @staticmethod
    def create(settings: SnomedSettings | None = None) -> SnomedClient:
        resolved = settings or load_settings().snomed

        if resolved.provider == PROVIDER_SNOWSTORM:
            from app.snomed.snowstorm_client import SnowstormClient

            return SnowstormClient(resolved)

        if resolved.provider == PROVIDER_MOCK:
            from app.snomed.mock_client import MockSnomedClient

            return MockSnomedClient(resolved)

        raise ValueError(
            MSG_INVALID_SNOMED_PROVIDER.format(provider=resolved.provider),
        )
