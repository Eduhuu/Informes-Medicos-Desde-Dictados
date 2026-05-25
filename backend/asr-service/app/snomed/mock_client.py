from app.config.settings import SnomedSettings
from app.models.snomed import SnomedConceptItem, SnomedSearchResult, SnomedTerm
from app.snomed.base import SnomedClient


class MockSnomedClient(SnomedClient):
    """Fixed SNOMED responses for local development without Snowstorm."""

    def __init__(self, settings: SnomedSettings) -> None:
        self._settings = settings

    def search_concepts(self, term: str) -> SnomedSearchResult:
        concept = SnomedConceptItem(
            conceptId="13645005",
            active=True,
            definitionStatus="FULLY_DEFINED",
            moduleId="900000000000207008",
            effectiveTime="20020131",
            fsn=SnomedTerm(
                term=f"Mock concept for {term} (disorder)",
                lang="en",
            ),
            pt=SnomedTerm(term=f"Mock concept for {term}", lang="en"),
            id="13645005",
            idAndFsnTerm=(
                f"13645005 | Mock concept for {term} (disorder) |"
            ),
        )
        return SnomedSearchResult(
            items=[concept],
            total=1,
            limit=self._settings.limit,
            offset=0,
            error=None,
        )
