import sys
from pathlib import Path

# Allow importing shared constants from repository root
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.config.settings import AsrSettings, load_settings
from app.constants.messages import MSG_INVALID_PROVIDER
from app.providers.base import ASRProvider
from app.providers.mock_provider import MockProvider
from shared.constants.AsrConstants import PROVIDER_MOCK, PROVIDER_WHISPER


class ASRFactory:
    """Builds and caches the active ASR provider from configuration."""

    @staticmethod
    def create(settings: AsrSettings | None = None) -> ASRProvider:
        resolved = settings or load_settings()

        if resolved.provider == PROVIDER_WHISPER:
            from app.providers.whisper_provider import WhisperProvider

            return WhisperProvider(
                model_name=resolved.model,
                device=resolved.device,
                language=resolved.language,
                compute_type=resolved.compute_type,
            )

        if resolved.provider == PROVIDER_MOCK:
            return MockProvider(device=resolved.device)

        raise ValueError(MSG_INVALID_PROVIDER.format(provider=resolved.provider))

    @staticmethod
    def create_and_preload(settings: AsrSettings | None = None) -> ASRProvider:
        provider = ASRFactory.create(settings)
        provider.preload()
        return provider
