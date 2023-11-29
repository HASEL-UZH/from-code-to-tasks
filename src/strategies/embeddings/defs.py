from typing import Protocol, Any, Callable, List


class IEmbeddingStrategy(Protocol):
    name: str

    def create_embedding(self, text) -> Any:
        ...

    def calculate_simularity(self, embedding1: Any, embedding2: Any) -> float:
        ...


class IEmbeddingStrategyFactory(Protocol):
    def create_embedding_strategy(
        self, content_provider: Callable[[], List[str]]
    ) -> IEmbeddingStrategy:
        ...
