import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.pln.base import PLNModel
from shared.constants.PlnConstants import (
    PLN_SOURCE_FARMACOS,
    PLN_SOURCE_MEDICAL,
)


def _spans_overlap(
    entity_a: dict[str, Any],
    entity_b: dict[str, Any],
) -> bool:
    return entity_a["start"] < entity_b["end"] and entity_b["start"] < entity_a["end"]


def _tag_entities(
    entities: list[dict[str, Any]],
    pln_source: str,
) -> list[dict[str, Any]]:
    tagged: list[dict[str, Any]] = []
    for entity in entities:
        tagged_entity = dict(entity)
        tagged_entity["pln_source"] = pln_source
        tagged.append(tagged_entity)
    return tagged


def merge_entities_prefer_farmacos(
    medical_entities: list[dict[str, Any]],
    farmacos_entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep all farmacos entities; drop medical entities that overlap any farmacos span."""
    merged = list(farmacos_entities)
    for medical_entity in medical_entities:
        overlaps_farmacos = any(
            _spans_overlap(medical_entity, farmacos_entity)
            for farmacos_entity in farmacos_entities
        )
        if not overlaps_farmacos:
            merged.append(medical_entity)
    return sorted(merged, key=lambda entity: (entity["start"], entity["end"]))


class PlnOrchestrator:
    """Runs medical and farmacos PLN models in parallel and merges their output."""

    def __init__(
        self,
        medical: PLNModel,
        farmacos: PLNModel,
        executor: ThreadPoolExecutor,
    ) -> None:
        self._medical = medical
        self._farmacos = farmacos
        self._executor = executor

    async def process_text(self, text: str) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()
        medical_future = loop.run_in_executor(
            self._executor,
            self._medical.process,
            text,
        )
        farmacos_future = loop.run_in_executor(
            self._executor,
            self._farmacos.process,
            text,
        )
        medical_raw, farmacos_raw = await asyncio.gather(
            medical_future,
            farmacos_future,
        )
        medical_tagged = _tag_entities(medical_raw, PLN_SOURCE_MEDICAL)
        farmacos_tagged = _tag_entities(farmacos_raw, PLN_SOURCE_FARMACOS)
        return merge_entities_prefer_farmacos(medical_tagged, farmacos_tagged)
