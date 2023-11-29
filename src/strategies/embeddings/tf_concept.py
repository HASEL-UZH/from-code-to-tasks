from typing import Any, Callable, List, Optional
from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import CountVectorizer
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


class TfEmbeddingStrategy(IEmbeddingStrategy):
    def __init__(
        self, tokenizer: ITokenizer, content_provider: Callable[[], List[str]]
    ):
        self._tokenizer = tokenizer
        self._content_provider = content_provider
        self._vectorizer: CountVectorizer = None
        self.name = "tf-embedding--" + tokenizer.name

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
                "TF concept cosine similarity calculation - ZeroDivision Error"
            )
        similarity = nominator / denominator
        return similarity

    def _ensure_vectorizer(self):
        if not self._vectorizer:
            self._vectorizer = CountVectorizer()
            content = " ".join(self._content_provider())
            corpus_tokens = self._tokenizer.tokenize(content)
            log.debug(
                f"TfEmbeddingStrategy.create_embedding ({self.name}), create corpus: {corpus_tokens[0:10]}"
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


class TfEmbeddingStrategyFactory(IEmbeddingStrategyFactory):
    def __init__(self, tokenizer: ITokenizer):
        self._tokenizer = tokenizer

    def create_embedding_strategy(
        self, content_provider: Callable[[], List[str]]
    ) -> IEmbeddingStrategy:
        return TfEmbeddingStrategy(self._tokenizer, content_provider)


class TfConcept(IEmbeddingConcept):
    name = "tf"

    def __init__(self):
        self.embedding_strategies = []
        self.content_strategies = ContentStrategies.TfxCore
        self.cache_strategy = CacheStrategy.Memory
        # self.embedding_strategies.append(
        #     TfEmbeddingStrategyFactory(StandardTokenizer())
        # )
        self.embedding_strategies.append(
            TfEmbeddingStrategyFactory(SubwordTokenizerNoNumbers())
        )
        # self.embedding_strategies.append(TfEmbeddingStrategyFactory(StandardTokenizerNoNumbers()))
        # self.embedding_strategies.append(TfEmbeddingStrategyFactory(SubwordTokenizer()))
        # self.embedding_strategies.append(TfEmbeddingStrategyFactory(SubwordTokenizerNoNumbers()))
        # self.embedding_strategies.append(TfEmbeddingStrategyFactory(NltkTokenizer()))
        # self.embedding_strategies.append(
        #     TfEmbeddingStrategyFactory(NltkTokenizerOptimized())
        # )
