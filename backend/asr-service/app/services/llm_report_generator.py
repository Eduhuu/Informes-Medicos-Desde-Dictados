from pathlib import Path

import httpx

from app.config.settings import LlmSettings
from app.constants.messages import (
    MSG_LLM_CONNECTION_ERROR,
    MSG_LLM_GENERATION_ERROR,
    MSG_LLM_REPORT_NOT_FOUND,
)
from app.services.report_paths import (
    control_report_path,
    ensure_session_reports_dir,
    llm_report_path,
)
from shared.constants.LlmConstants import (
    OLLAMA_CHAT_PATH,
    OLLAMA_ROLE_SYSTEM,
    OLLAMA_ROLE_USER,
)


class LlmReportGenerator:
    """Reads a session report and generates a structured medical report via Ollama."""

    def __init__(self, settings: LlmSettings, reports_dir: Path) -> None:
        self._settings = settings
        self._reports_dir = reports_dir

    @property
    def enabled(self) -> bool:
        return self._settings.enabled

    async def generate(self, session_id: str) -> str:
        session_report_path = control_report_path(self._reports_dir, session_id)
        if not session_report_path.exists():
            raise FileNotFoundError(
                MSG_LLM_REPORT_NOT_FOUND.format(session_id=session_id),
            )

        session_report_content = session_report_path.read_text(encoding="utf-8")
        generated_report = await self._call_ollama(session_report_content)

        ensure_session_reports_dir(self._reports_dir, session_id)
        output_path = llm_report_path(self._reports_dir, session_id)
        output_path.write_text(generated_report, encoding="utf-8")

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
