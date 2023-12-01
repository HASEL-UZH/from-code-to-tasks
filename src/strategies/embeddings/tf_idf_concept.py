from typing import Any, Optional

from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer

from src.strategies.defs import (
    ContentStrategies,
    CacheStrategy,
    IEmbeddingConcept,
)
from src.strategies.embeddings.defs import IEmbeddingStrategy
from src.strategies.tokenization.defs import ITokenizer
from src.strategies.tokenization.tokenizer import SubwordTokenizer, StandardTokenizer


class TfIdfEmbeddingStrategy(IEmbeddingStrategy):
    def __init__(self, tokenizer: ITokenizer):
        self._tokenizer = tokenizer
        self._vectorizer: Optional[TfidfVectorizer] = None
        self.name = "tf-idf-embedding--" + tokenizer.name
        self._cache = {}

    def init(self, corpus_texts: [str]) -> [str]:
        self._cache = {}
        self._vectorizer = TfidfVectorizer()
        tokenized_corpus_text = self._tokenizer.tokenize_corpus_texts(corpus_texts)
        # log.debug(
        #     f"TfIdfEmbeddingStrategy.create_embedding ({self.name}), create corpus: {corpus_tokens[0:10]}"
        # )
        X = self._vectorizer.fit_transform(tokenized_corpus_text)
        shape = X.shape
        feature_names = self._vectorizer.get_feature_names_out()
        return feature_names

    # def init(self, corpus_texts: [str]) -> [str]:
    #     self._cache = {}
    #     self._vectorizer = TfidfVectorizer()
    #     X = self._vectorizer.fit_transform(corpus_texts)
    #     feature_names = self._vectorizer.get_feature_names_out()
    #     return feature_names

    def get_embedding(self, text) -> Any:
        embedding = self._cache.get(text)
        if embedding is None:
            embedding = self._create_embedding(text)
            self._cache[text] = embedding
        return embedding

    def _create_embedding(self, text) -> Any:
        tokens = self._tokenizer.tokenize(text)
        token_text = " ".join(tokens)
        tf_idf_text_vector = self._vectorizer.transform([token_text]).toarray()[0]
        return tf_idf_text_vector

    def calculate_simularity(self, embedding1: Any, embedding2: Any) -> float:
        nominator = dot(embedding1, embedding2)
        denominator = norm(embedding1) * norm(embedding2)
        if denominator == 0:
            raise Exception(
                "TF-IDF concept cosine similarity calculation - ZeroDivision Error"
            )
        similarity = nominator / denominator
        return similarity

    def get_tokens(self, text: str) -> [str]:
        return self._tokenizer.tokenize(text)


class TfIdfConcept(IEmbeddingConcept):
    name = "tf_idf"

    def __init__(self):
        self.embedding_strategies = []
        self.content_strategies = ContentStrategies.TfxCore
        self.cache_strategy = CacheStrategy.Memory
        self.embedding_strategies.append(TfIdfEmbeddingStrategy(StandardTokenizer()))
        self.embedding_strategies.append(TfIdfEmbeddingStrategy(SubwordTokenizer()))
