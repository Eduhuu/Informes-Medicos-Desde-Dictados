from typing import Any

import httpx

from app.constants.messages import MSG_CONCEPT_MAP_LOOKUP_FAILED
from app.models.concept_map import ConceptMapMatch, ConceptMapTranslation
from shared.constants.FhirConceptMapConstants import (
    CODING_KEY_CODE,
    CODING_KEY_DISPLAY,
    CODING_KEY_SYSTEM,
    FHIR_SNOMED_SYSTEM,
    FHIR_TRANSLATE_PATH,
    FHIR_VALUESET_EXPAND_PATH,
    PARAM_KEY_NAME,
    PARAM_KEY_PARAMETER,
    PARAM_KEY_PART,
    PARAM_NAME_MATCH,
    PARAM_NAME_RESULT,
    PART_NAME_CONCEPT,
    PART_NAME_EQUIVALENCE,
    PART_VALUE_BOOLEAN,
    PART_VALUE_CODE,
    PART_VALUE_CODING,
    TRANSLATE_HEADER_ACCEPT_LANGUAGE,
    TRANSLATE_PARAM_CODE,
    TRANSLATE_PARAM_SYSTEM,
    TRANSLATE_PARAM_URL,
    TRANSLATION_SOURCE_CM_FALLBACK,
    TRANSLATION_SOURCE_CM_PRIMARY,
    TRANSLATION_SOURCE_VALUESET_EXPAND,
    VALUESET_KEY_CODE,
    VALUESET_KEY_CONTAINS,
    VALUESET_KEY_DISPLAY,
    VALUESET_KEY_EXPANSION,
    VALUESET_KEY_SYSTEM,
    VALUESET_PARAM_FILTER,
    VALUESET_PARAM_URL,
)


class FhirConceptMapClient:
    """Translates SNOMED codes to ICD-10 using a three-step fallback chain:
    1. ConceptMap $translate with primary map (6011000124106)
    2. ConceptMap $translate with fallback map (447562003)
    3. ValueSet $expand with the entity term as filter
    """

    def __init__(
        self,
        *,
        enabled: bool,
        base_url: str,
        concept_map_url: str,
        concept_map_fallback_url: str,
        value_set_expand_url: str,
        timeout_seconds: float,
        language: str,
    ) -> None:
        self._enabled = enabled
        self._translate_url = f"{base_url.rstrip('/')}/{FHIR_TRANSLATE_PATH}"
        self._valueset_expand_url = f"{base_url.rstrip('/')}/{FHIR_VALUESET_EXPAND_PATH}"
        self._concept_map_url = concept_map_url
        self._concept_map_fallback_url = concept_map_fallback_url
        self._value_set_expand_url = value_set_expand_url
        self._timeout_seconds = timeout_seconds
        self._language = language

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def translate(self, concept_id: str, term: str) -> ConceptMapTranslation:
        """Try the full fallback chain and return the first successful translation."""
        headers = {TRANSLATE_HEADER_ACCEPT_LANGUAGE: self._language}

        result = await self._call_concept_map(
            concept_id=concept_id,
            concept_map_url=self._concept_map_url,
            source=TRANSLATION_SOURCE_CM_PRIMARY,
            headers=headers,
        )
        if result.result:
            return result

        result = await self._call_concept_map(
            concept_id=concept_id,
            concept_map_url=self._concept_map_fallback_url,
            source=TRANSLATION_SOURCE_CM_FALLBACK,
            headers=headers,
        )
        if result.result:
            return result

        return await self._call_valueset_expand(term=term, headers=headers)

    async def _call_concept_map(
        self,
        *,
        concept_id: str,
        concept_map_url: str,
        source: str,
        headers: dict[str, str],
    ) -> ConceptMapTranslation:
        params = {
            TRANSLATE_PARAM_CODE: concept_id,
            TRANSLATE_PARAM_SYSTEM: FHIR_SNOMED_SYSTEM,
            TRANSLATE_PARAM_URL: concept_map_url,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(
                    self._translate_url,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                return _parse_parameters(response.json(), source=source)
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return ConceptMapTranslation(
                result=False,
                matches=[],
                error=MSG_CONCEPT_MAP_LOOKUP_FAILED.format(concept_id=concept_id),
                source=source,
            )

    async def _call_valueset_expand(
        self,
        *,
        term: str,
        headers: dict[str, str],
    ) -> ConceptMapTranslation:
        params = {
            VALUESET_PARAM_URL: self._value_set_expand_url,
            VALUESET_PARAM_FILTER: term,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(
                    self._valueset_expand_url,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                return _parse_value_set_expansion(response.json())
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return ConceptMapTranslation(
                result=False,
                matches=[],
                source=TRANSLATION_SOURCE_VALUESET_EXPAND,
            )


def _parse_parameters(data: dict[str, Any], *, source: str) -> ConceptMapTranslation:
    parameters: list[dict[str, Any]] = data.get(PARAM_KEY_PARAMETER, [])

    result = False
    matches: list[ConceptMapMatch] = []

    for param in parameters:
        name = param.get(PARAM_KEY_NAME)

        if name == PARAM_NAME_RESULT:
            result = bool(param.get(PART_VALUE_BOOLEAN, False))

        elif name == PARAM_NAME_MATCH:
            match = _parse_match_parts(param.get(PARAM_KEY_PART, []))
            if match is not None:
                matches.append(match)

    return ConceptMapTranslation(result=result, matches=matches, source=source)


def _parse_match_parts(parts: list[dict[str, Any]]) -> ConceptMapMatch | None:
    equivalence = ""
    code = ""
    system = ""
    display = ""

    for part in parts:
        name = part.get(PARAM_KEY_NAME)

        if name == PART_NAME_EQUIVALENCE:
            equivalence = str(part.get(PART_VALUE_CODE, ""))

        elif name == PART_NAME_CONCEPT:
            coding: dict[str, Any] = part.get(PART_VALUE_CODING, {})
            code = str(coding.get(CODING_KEY_CODE, ""))
            system = str(coding.get(CODING_KEY_SYSTEM, ""))
            display = str(coding.get(CODING_KEY_DISPLAY, ""))

    if not code:
        return None

    return ConceptMapMatch(
        equivalence=equivalence,
        code=code,
        system=system,
        display=display,
    )


def _parse_value_set_expansion(data: dict[str, Any]) -> ConceptMapTranslation:
    expansion: dict[str, Any] = data.get(VALUESET_KEY_EXPANSION, {})
    contains: list[dict[str, Any]] = expansion.get(VALUESET_KEY_CONTAINS, [])

    matches: list[ConceptMapMatch] = []
    for item in contains:
        code = str(item.get(VALUESET_KEY_CODE, ""))
        if not code:
            continue
        matches.append(
            ConceptMapMatch(
                equivalence="",
                code=code,
                system=str(item.get(VALUESET_KEY_SYSTEM, "")),
                display=str(item.get(VALUESET_KEY_DISPLAY, "")),
            ),
        )

    return ConceptMapTranslation(
        result=bool(matches),
        matches=matches,
        source=TRANSLATION_SOURCE_VALUESET_EXPAND,
    )
