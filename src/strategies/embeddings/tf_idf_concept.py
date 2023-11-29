from typing import Any, Callable, List, Optional
from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer

from src.core.logger import log
from src.strategies.tokenization.nltk_tokenizer import (
    NltkTokenizer,
    NltkTokenizerOptimized,
)
from src.strategies.tokenization.standard_tokenizer import (
    StandardTokenizer,
)
from src.strategies.defs import (
    ContentStrategies,
    CacheStrategy,
    IEmbeddingConcept,
)
from src.strategies.embeddings.defs import IEmbeddingStrategy, IEmbeddingStrategyFactory
from src.strategies.tokenization.defs import ITokenizer
from src.strategies.tokenization.subword_tokenizer import SubwordTokenizerNoNumbers


class TfIdfEmbeddingStrategy(IEmbeddingStrategy):
    def __init__(
        self, tokenizer: ITokenizer, content_provider: Callable[[], List[str]]
    ):
        self._tokenizer = tokenizer
        self._content_provider = content_provider
        self._vectorizer: TfidfVectorizer = None
        self.name = "tf-idf-embedding--" + tokenizer.name

    def create_embedding(self, text) -> Any:
        self._ensure_vectorizer()

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

    def _ensure_vectorizer(self):
        if not self._vectorizer:
            self._vectorizer = TfidfVectorizer()
            corpus_tokens = self._get_corpus_tokens()
            log.debug(
                f"TfIdfEmbeddingStrategy.create_embedding ({self.name}), create corpus: {corpus_tokens[0:10]}"
            )
            X = self._vectorizer.fit_transform(corpus_tokens)
            # shape = X.shape
            # feature_names = self._vectorizer.get_feature_names_out()
            return corpus_tokens
        return None

    def _get_corpus_tokens(self) -> [str]:
        content = " ".join(self._content_provider())
        corpus_tokens = self._tokenizer.tokenize(content)
        return corpus_tokens

    def get_corpus(self) -> Optional[str]:
        tokens = self._ensure_vectorizer()
        if not tokens:
            tokens = self._get_corpus_tokens()
        return "\n".join(tokens)


class TfIdfEmbeddingStrategyFactory(IEmbeddingStrategyFactory):
    def __init__(self, tokenizer: ITokenizer):
        self._tokenizer = tokenizer

    def create_embedding_strategy(
        self, content_provider: Callable[[], List[str]]
    ) -> IEmbeddingStrategy:
        return TfIdfEmbeddingStrategy(self._tokenizer, content_provider)


class TfIdfConcept(IEmbeddingConcept):
    name = "tf_idf"

    def __init__(self):
        self.embedding_strategies = []
        self.content_strategies = ContentStrategies.TfxCore
        self.cache_strategy = CacheStrategy.Memory
        # self.embedding_strategies.append(
        #     TfIdfEmbeddingStrategyFactory(StandardTokenizer())
        # )
        # self.embedding_strategies.append(
        #     TfIdfEmbeddingStrategyFactory(SubwordTokenizerNoNumbers())
        # )
        # self.embedding_strategies.append(TfIdfEmbeddingStrategyFactory(StandardTokenizerNoNumbers()))
        # self.embedding_strategies.append(TfIdfEmbeddingStrategyFactory(SubwordTokenizer()))
        self.embedding_strategies.append(
            TfIdfEmbeddingStrategyFactory(SubwordTokenizerNoNumbers())
        )
        # self.embedding_strategies.append(TfIdfEmbeddingStrategyFactory(NltkTokenizer()))
        self.embedding_strategies.append(
            TfIdfEmbeddingStrategyFactory(NltkTokenizerOptimized())
        )
