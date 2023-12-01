from typing import Any, Optional

from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import CountVectorizer

from src.core.logger import log
from src.strategies.defs import (
    ContentStrategies,
    CacheStrategy,
    IEmbeddingConcept,
)
from src.strategies.embeddings.defs import IEmbeddingStrategy
from src.strategies.tokenization.defs import ITokenizer
from src.strategies.tokenization.tokenizer import SubwordTokenizer, StandardTokenizer


class TfEmbeddingStrategy(IEmbeddingStrategy):
    def __init__(self, tokenizer: ITokenizer):
        self._tokenizer = tokenizer
        self._vectorizer: Optional[CountVectorizer] = None
        self.name = "tf-embedding--" + tokenizer.name
        self._cache = {}

    def init(self, corpus_text: [str]) -> [str]:
        self._cache = {}
        self._vectorizer = CountVectorizer()

        content = " ".join(corpus_text)
        corpus_tokens = self._tokenizer.tokenize(content)
        log.debug(
            f"TfEmbeddingStrategy.create_embedding ({self.name}), create corpus: {corpus_tokens[0:10]}"
        )
        X = self._vectorizer.fit_transform(corpus_tokens)
        # shape = X.shape
        # feature_names = self._vectorizer.get_feature_names_out()
        return corpus_tokens

    def get_embedding(self, text) -> Any:
        embedding = self._cache.get(text)
        if embedding is not None:
            embedding = self._create_embedding(text)
            self._cache[text] = embedding
        return embedding

    def _create_embedding(self, text) -> Any:
        tokens = self._tokenizer.tokenize(text)
        token_text = " ".join(tokens)
        tf_text_vector = self._vectorizer.transform([token_text]).toarray()[0]
        return tf_text_vector

    def calculate_simularity(self, embedding1: Any, embedding2: Any) -> float:
        nominator = dot(embedding1, embedding2)
        denominator = norm(embedding1) * norm(embedding2)
        if denominator == 0:
            raise Exception(
                "TF concept cosine similarity calculation - ZeroDivision Error"
            )
        similarity = nominator / denominator
        return similarity

    def get_tokens(self, text: str) -> [str]:
        return self._tokenizer.tokenize(text)


class TfConcept(IEmbeddingConcept):
    name = "tf"

    def __init__(self):
        self.embedding_strategies = []
        self.content_strategies = ContentStrategies.TfxCore
        self.cache_strategy = CacheStrategy.Memory
        self.embedding_strategies.append(TfEmbeddingStrategy(StandardTokenizer()))
        self.embedding_strategies.append(TfEmbeddingStrategy(SubwordTokenizer()))
