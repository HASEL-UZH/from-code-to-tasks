from typing import Protocol, Any, Callable, List, Optional


class IEmbeddingStrategy(Protocol):
    name: str

    def init(self, corpus_text: [str]) -> [str]:
        """
        Initializes the strategy with the given corpus text and returns the tokens used to build the internal corpus
        """

    def get_embedding(self, text) -> Any:
        ...

    def calculate_simularity(self, embedding1: Any, embedding2: Any) -> float:
        ...

    def get_tokens(self, text: str) -> [str]:
        return None


class IEmbeddingStrategyFactory(Protocol):
    def create_embedding_strategy(
        self, content_provider: Callable[[], List[str]]
    ) -> IEmbeddingStrategy:
        ...
