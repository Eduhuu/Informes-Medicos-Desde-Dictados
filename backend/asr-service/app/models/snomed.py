from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class SnomedTerm:
    term: str
    lang: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SnomedTerm":
        return cls(term=str(data["term"]), lang=str(data["lang"]))


@dataclass
class SnomedConceptItem:
    conceptId: str
    active: bool
    definitionStatus: str
    moduleId: str
    effectiveTime: str
    fsn: SnomedTerm
    pt: SnomedTerm
    id: str
    idAndFsnTerm: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SnomedConceptItem":
        return cls(
            conceptId=str(data["conceptId"]),
            active=bool(data["active"]),
            definitionStatus=str(data["definitionStatus"]),
            moduleId=str(data["moduleId"]),
            effectiveTime=str(data["effectiveTime"]),
            fsn=SnomedTerm.from_dict(data["fsn"]),
            pt=SnomedTerm.from_dict(data["pt"]),
            id=str(data["id"]),
            idAndFsnTerm=str(data["idAndFsnTerm"]),
        )


@dataclass
class SnomedSearchResult:
    items: list[SnomedConceptItem] = field(default_factory=list)
    total: int = 0
    limit: int = 0
    offset: int = 0
    searchAfter: Optional[str] = None
    searchAfterArray: Optional[list[int]] = None
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if payload.get("searchAfter") is None:
            payload.pop("searchAfter", None)
        if payload.get("searchAfterArray") is None:
            payload.pop("searchAfterArray", None)
        return payload

    @classmethod
    def from_snowstorm_response(
        cls,
        data: dict[str, Any],
        *,
        default_limit: int,
    ) -> "SnomedSearchResult":
        items = [
            SnomedConceptItem.from_dict(item)
            for item in data.get("items", [])
        ]
        search_after_array = data.get("searchAfterArray")
        return cls(
            items=items,
            total=int(data.get("total", 0)),
            limit=int(data.get("limit", default_limit)),
            offset=int(data.get("offset", 0)),
            searchAfter=data.get("searchAfter"),
            searchAfterArray=(
                list(search_after_array) if search_after_array is not None else None
            ),
            error=None,
        )

    @classmethod
    def failure(cls, *, term: str, limit: int, message: str) -> "SnomedSearchResult":
        return cls(
            items=[],
            total=0,
            limit=limit,
            offset=0,
            error=message.format(term=term),
        )


@dataclass
class EnrichedEntity:
    word: str
    score: float
    entity_group: str
    start: int
    end: int
    snomed: SnomedSearchResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "word": self.word,
            "score": self.score,
            "entity_group": self.entity_group,
            "start": self.start,
            "end": self.end,
            "snomed": self.snomed.to_dict(),
        }

    @classmethod
    def from_ner_entity(
        cls,
        ner_entity: dict[str, Any],
        snomed_result: SnomedSearchResult,
    ) -> "EnrichedEntity":
        return cls(
            word=str(ner_entity["word"]),
            score=float(ner_entity["score"]),
            entity_group=str(ner_entity["entity_group"]),
            start=int(ner_entity["start"]),
            end=int(ner_entity["end"]),
            snomed=snomed_result,
        )
