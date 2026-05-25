from abc import ABC, abstractmethod

from app.models.snomed import SnomedSearchResult


class SnomedClient(ABC):
    """Strategy interface for interchangeable SNOMED terminology clients."""

    @abstractmethod
    def search_concepts(self, term: str) -> SnomedSearchResult:
        """Search SNOMED CT concepts by term."""
