import httpx

from app.config.settings import SnomedSettings
from app.constants.messages import MSG_SNOMED_LOOKUP_FAILED
from app.models.snomed import SnomedSearchResult
from app.snomed.base import SnomedClient
from shared.constants.SnomedConstants import (
    QUERY_PARAM_ACTIVE,
    QUERY_PARAM_LIMIT,
    QUERY_PARAM_PREFERRED_LANGUAGE,
    QUERY_PARAM_TERM,
    SNOMED_CONCEPTS_PATH_SUFFIX,
)


class SnowstormClient(SnomedClient):
    """SNOMED CT client backed by the Snowstorm REST API."""

    def __init__(self, settings: SnomedSettings) -> None:
        self._settings = settings
        self._concepts_url = (
            f"{settings.base_url.rstrip('/')}/"
            f"{settings.branch.strip('/')}/"
            f"{SNOMED_CONCEPTS_PATH_SUFFIX}"
        )

    def search_concepts(self, term: str) -> SnomedSearchResult:
        params = {
            QUERY_PARAM_TERM: term,
            QUERY_PARAM_ACTIVE: str(self._settings.active).lower(),
            QUERY_PARAM_PREFERRED_LANGUAGE: self._settings.preferred_language,
            QUERY_PARAM_LIMIT: self._settings.limit,
        }

        try:
            with httpx.Client(timeout=self._settings.timeout_seconds) as client:
                response = client.get(self._concepts_url, params=params)
                response.raise_for_status()
                return SnomedSearchResult.from_snowstorm_response(
                    response.json(),
                    default_limit=self._settings.limit,
                )
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return SnomedSearchResult.failure(
                term=term,
                limit=self._settings.limit,
                message=MSG_SNOMED_LOOKUP_FAILED,
            )
