from typing import Protocol, Any, Callable, List, Optional


class IEmbeddingStrategy(Protocol):
    name: str

    def create_embedding(self, text) -> Any:
        ...

    def calculate_simularity(self, embedding1: Any, embedding2: Any) -> float:
        ...

    def get_corpus(self) -> Optional[str]:
        """
        Retrieves the corpus data used by the embedding strategy.

        This method provides a default implementation that can be overridden
        by concrete implementations of the IEmbeddingStrategy protocol.
        The method should return the corpus data in a format suitable for
        the embedding strategy, or None if not applicable.

        Returns:
            Any: The corpus data used by the embedding strategy, or None
            if the corpus is not defined or not applicable for this strategy.
        """
        return None


class IEmbeddingStrategyFactory(Protocol):
    def create_embedding_strategy(
        self, content_provider: Callable[[], List[str]]
    ) -> IEmbeddingStrategy:
        ...
