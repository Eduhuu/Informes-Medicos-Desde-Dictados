import sys
from pathlib import Path
# Allow importing shared constants from repository root
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


from app.pln.base import PLNModel
from app.config.settings import PlnSettings, load_settings
from shared.constants.PlnConstants import PLN_MODEL_RIGONSALLAUKA

class PNLFactory:
    """Builds and caches the active PNL model from configuration."""
    @staticmethod
    def create(settings: PlnSettings | None = None) -> PLNModel:
        resolved = settings or load_settings()

        if(resolved.model == PLN_MODEL_RIGONSALLAUKA):
            print("Creating RigonsallaukaPLN model")
            from app.pln.RigonsallaukaPLN import RigonsallaukaPLN
            return RigonsallaukaPLN(settings.model, settings.aggregation_strategy, settings.task)
        else:
            raise ValueError(f"Unsupported PNL model: {resolved.model}")

    @staticmethod
    def create_and_preload(settings: PlnSettings | None = None) -> PLNModel:
        model = PNLFactory.create(settings)
        print("Preloading PNL model")
        model.preload()
        return model