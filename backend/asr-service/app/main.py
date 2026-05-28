import sys
from concurrent.futures import ThreadPoolExecutor
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
from app.factory.snomed_factory import SnomedFactory
from app.services.pln_orchestrator import PlnOrchestrator
from app.services.session_report import SessionReportWriter
from shared.constants.PlnConstants import PLN_EXECUTOR_MAX_WORKERS


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()

    provider = ASRFactory.create_and_preload(settings.asr)
    pln_medical = PNLFactory.create_and_preload(settings.pln_medical)
    pln_farmacos = PNLFactory.create_and_preload(settings.pln_farmacos)
    pln_executor = ThreadPoolExecutor(max_workers=PLN_EXECUTOR_MAX_WORKERS)
    pln_orchestrator = PlnOrchestrator(
        pln_medical,
        pln_farmacos,
        pln_executor,
    )
    snomed_client = SnomedFactory.create(settings.snomed)
    session_report_writer = SessionReportWriter(
        settings.reports.directory,
        enabled=settings.reports.enabled,
    )

    app.state.asr_settings = settings.asr
    app.state.pln_medical_settings = settings.pln_medical
    app.state.pln_farmacos_settings = settings.pln_farmacos
    app.state.snomed_settings = settings.snomed
    app.state.report_settings = settings.reports

    app.state.asr_provider = provider
    app.state.pln_orchestrator = pln_orchestrator
    app.state.pln_executor = pln_executor
    app.state.snomed_client = snomed_client
    app.state.session_report_writer = session_report_writer

    yield

    app.state.asr_settings = None
    app.state.pln_medical_settings = None
    app.state.pln_farmacos_settings = None
    app.state.snomed_settings = None
    app.state.report_settings = None

    app.state.asr_provider = None
    app.state.pln_orchestrator = None
    pln_executor.shutdown(wait=False)
    app.state.pln_executor = None
    app.state.snomed_client = None
    app.state.session_report_writer = None


app = FastAPI(
    title="ASR Service",
    description="Transcripción de fragmentos de audio con motor intercambiable",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)
