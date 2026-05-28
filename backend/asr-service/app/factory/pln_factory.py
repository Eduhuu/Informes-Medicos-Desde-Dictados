import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.config.settings import PlnSettings, load_settings
from app.pln.TransformersPipelinePLN import TransformersPipelinePLN
from app.pln.base import PLNModel
from shared.constants.PlnConstants import SUPPORTED_PLN_MODELS


class PNLFactory:
    """Builds and caches PLN models from configuration."""

    @staticmethod
    def create(settings: PlnSettings | None = None) -> PLNModel:
        resolved = settings
        if resolved is None:
            resolved = load_settings().pln_medical

        if resolved.model not in SUPPORTED_PLN_MODELS:
            raise ValueError(f"Unsupported PLN model: {resolved.model}")

        return TransformersPipelinePLN(
            resolved.model,
            resolved.aggregation_strategy,
            resolved.task,
        )

    @staticmethod
    def create_and_preload(settings: PlnSettings | None = None) -> PLNModel:
        model = PNLFactory.create(settings)
        model.preload()
        return model
