import re
from pathlib import Path

import httpx

from app.config.settings import LlmSettings
from app.constants.messages import (
    MSG_LLM_CONNECTION_ERROR,
    MSG_LLM_GENERATION_ERROR,
    MSG_LLM_REPORT_NOT_FOUND,
)
from shared.constants.LlmConstants import (
    LLM_REPORT_FILENAME_PREFIX,
    LLM_REPORT_FILENAME_SUFFIX,
    OLLAMA_CHAT_PATH,
    OLLAMA_ROLE_SYSTEM,
    OLLAMA_ROLE_USER,
)
from shared.constants.ReportConstants import REPORT_FILENAME_PREFIX, REPORT_FILENAME_SUFFIX

_SAFE_SESSION_ID_PATTERN = re.compile(r"[^\w\-]+")


class LlmReportGenerator:
    """Reads a session report and generates a structured medical report via Ollama."""

    def __init__(self, settings: LlmSettings, reports_dir: Path) -> None:
        self._settings = settings
        self._reports_dir = reports_dir

    @property
    def enabled(self) -> bool:
        return self._settings.enabled

    async def generate(self, session_id: str) -> str:
        print(f"Generating LLM report for session {session_id}")
        session_report_path = self._session_report_path(session_id)
        print(f"Session report path: {session_report_path}")
        if not session_report_path.exists():
            raise FileNotFoundError(
                MSG_LLM_REPORT_NOT_FOUND.format(session_id=session_id),
            )
        print(f"Session report exists: {session_report_path.exists()}")
        session_report_content = session_report_path.read_text(encoding="utf-8")
        generated_report = await self._call_ollama(session_report_content)

        llm_report_path = self._llm_report_path(session_id)
        llm_report_path.write_text(generated_report, encoding="utf-8")

        return generated_report

    async def _call_ollama(self, report_content: str) -> str:
        url = self._settings.base_url.rstrip("/") + OLLAMA_CHAT_PATH
        payload = {
            "model": self._settings.model,
            "stream": False,
            "messages": [
                {
                    "role": OLLAMA_ROLE_SYSTEM,
                    "content": self._settings.system_prompt,
                },
                {
                    "role": OLLAMA_ROLE_USER,
                    "content": report_content,
                },
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.timeout_seconds) as client:
                response = await client.post(url, json=payload)
                if not response.is_success:
                    body = response.text
                    raise RuntimeError(
                        MSG_LLM_GENERATION_ERROR.format(
                            error=f"HTTP {response.status_code} — {body}",
                        ),
                    )
        except httpx.ConnectError as exc:
            raise ConnectionError(
                MSG_LLM_CONNECTION_ERROR.format(error=str(exc)),
            ) from exc

        data = response.json()
        return str(data["message"]["content"])

    def _session_report_path(self, session_id: str) -> Path:
        safe_id = _SAFE_SESSION_ID_PATTERN.sub("_", session_id).strip("_") or "default"
        filename = f"{REPORT_FILENAME_PREFIX}{safe_id}{REPORT_FILENAME_SUFFIX}"
        return self._reports_dir / filename

    def _llm_report_path(self, session_id: str) -> Path:
        safe_id = _SAFE_SESSION_ID_PATTERN.sub("_", session_id).strip("_") or "default"
        filename = f"{LLM_REPORT_FILENAME_PREFIX}{safe_id}{LLM_REPORT_FILENAME_SUFFIX}"
        return self._reports_dir / filename
