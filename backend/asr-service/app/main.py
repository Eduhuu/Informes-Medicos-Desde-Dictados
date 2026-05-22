import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.api.routes import router
from app.config.settings import load_settings
from app.factory.asr_factory import ASRFactory
from app.factory.pln_factory import PNLFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()

    provider = ASRFactory.create_and_preload(settings.asr)
    pln_strategy = PNLFactory.create_and_preload(settings.pln)

    app.state.asr_settings = settings.asr
    app.state.pln_settings = settings.pln

    app.state.asr_provider = provider
    app.state.pln_provider = pln_strategy
    
    yield
    app.state.asr_settings = None
    app.state.pln_settings = None

    app.state.asr_provider = None
    app.state.pln_provider = None

app = FastAPI(
    title="ASR Service",
    description="Transcripción de fragmentos de audio con motor intercambiable",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)
