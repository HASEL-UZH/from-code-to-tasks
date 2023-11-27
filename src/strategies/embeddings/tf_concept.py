from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import CountVectorizer

from src.strategies.embeddings.defs import ContentStrategies, CacheStrategy


def _tf_embedding_strategy(vectorizer, text):
    tf_text_vector = vectorizer.transform([text]).toarray()[0]
    return tf_text_vector


def _create_strategy(corpus_provider):
    vectorizer = None

    def create_embedding(text):
        nonlocal vectorizer
        if not vectorizer:
            vectorizer = CountVectorizer()
            X = vectorizer.fit_transform(corpus_provider())
            shape = X.shape
            feature_names = vectorizer.get_feature_names_out()

        return _tf_embedding_strategy(vectorizer, text)

    return create_embedding


def _calculate_cosine_similarity(embedding1, embedding2):
    nominator = dot(embedding1, embedding2)
    denominator = norm(embedding1) * norm(embedding2)
    if denominator == 0:
        raise Exception("TF concept cosine similarity calculation - ZeroDivision Error")
    similarity = nominator / denominator
    return similarity


# corpus_providers: {java_corpus: ICorpusProvider, java_subword_corpus: ICorpusProvider}


def create_tf_concept(corpus_providers):
    strategies = []
    strategies.append(
        {
            "id": "corpus_standard_with_numbers",
            "create_embedding": _create_strategy(
                corpus_providers["corpus_standard_with_numbers"]
            ),
        }
    )
    # strategies.append(
    #     {
    #         "id": "corpus_standard_without_numbers",
    #         "create_embedding": _create_strategy(
    #             corpus_providers["corpus_standard_without_numbers"]
    #         ),
    #     }
    # )
    # strategies.append(
    #     {
    #         "id": "corpus_subword_with_numbers",
    #         "create_embedding": _create_strategy(
    #             corpus_providers["corpus_subword_with_numbers"]
    #         ),
    #     }
    # )
    # strategies.append(
    #     {
    #         "id": "corpus_subword_without_numbers",
    #         "create_embedding": _create_strategy(
    #             corpus_providers["corpus_subword_without_numbers"]
    #         ),
    #     }
    # )
    return {
        "id": "tf",
        "strategies": strategies,
        "calculate_similarity": _calculate_cosine_similarity,
        "content_strategies": ContentStrategies.Tfx,
        "cache_strategy": CacheStrategy.Memory,
    }
