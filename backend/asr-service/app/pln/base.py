from abc import ABC, abstractmethod

class PLNModel(ABC):
    """Strategy interface for interchangeable PNL model."""

    @abstractmethod
    def process(self, text: str) -> str:
        """Process a single text."""

    # @abstractmethod
    # def preload(self) -> None:
    #     """Optional hook to load models at startup (default: no-op)."""