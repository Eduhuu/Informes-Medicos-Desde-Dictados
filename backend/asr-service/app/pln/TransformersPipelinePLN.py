from typing import Any

from app.pln.base import PLNModel


class TransformersPipelinePLN(PLNModel):
    """Hugging Face transformers pipeline for NER / token-classification."""

    def __init__(self, model: str, aggregation_strategy: str, task: str) -> None:
        self._model_id = model
        self._aggregation_strategy = aggregation_strategy
        self._task = task
        self._pipeline: Any = None

    def preload(self) -> None:
        from transformers import pipeline

        self._pipeline = pipeline(
            self._task,
            model=self._model_id,
            aggregation_strategy=self._aggregation_strategy,
        )

    def process(self, text: str) -> list[dict[str, Any]]:
        if self._pipeline is None:
            raise RuntimeError("PLN model not preloaded")
        return self._pipeline(text)
