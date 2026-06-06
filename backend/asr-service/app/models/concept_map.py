from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class ConceptMapMatch:
    equivalence: str
    code: str
    system: str
    display: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConceptMapTranslation:
    result: bool
    matches: list[ConceptMapMatch] = field(default_factory=list)
    error: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "result": self.result,
            "matches": [m.to_dict() for m in self.matches],
        }
        if self.source is not None:
            payload["source"] = self.source
        if self.error is not None:
            payload["error"] = self.error
        return payload
