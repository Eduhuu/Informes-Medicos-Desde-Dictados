from abc import ABC, abstractmethod
from typing import Any

class PLNModel(ABC):
    """Strategy interface for interchangeable PNL model."""

    @abstractmethod
    def process(self, text: str) -> list[dict[str, Any]]:
        """Process a single text and return NER entities."""

    # @abstractmethod
    # def preload(self) -> None:
    #     """Optional hook to load models at startup (default: no-op)."""