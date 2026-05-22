from app.pln.base import PLNModel


class RigonsallaukaPLN(PLNModel):
    """Rigonsallauka spanish medical NER PLN model."""

    def __init__(self, model: str, aggregation_strategy: str, task: str) -> None:
        self._model = model
        self._aggregation_strategy = aggregation_strategy
        self._task = task
        return None

    def preload(self) -> None:
        from transformers import pipeline
        self._model = pipeline(
            self._task,
            model=self._model, 
            aggregation_strategy=self._aggregation_strategy
        )

    def process(self, text: str) -> str:
        return self._model(text) 
