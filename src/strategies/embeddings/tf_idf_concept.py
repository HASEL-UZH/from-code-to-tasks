from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer

from src.strategies.embeddings.embedding_strategies import get_java_corpus, get_java_corpus_subword


def _tf_idf_embedding_strategy(text, corpus):
    tf_idf_vectorizer = TfidfVectorizer()
    X = tf_idf_vectorizer.fit_transform(corpus)
    shape = X.shape
    feature_names = tf_idf_vectorizer.get_feature_names_out()
    tf_idf_text_vector = tf_idf_vectorizer.transform([text]).toarray()[0]
    return tf_idf_text_vector


def _create_strategy(corpus_provider):
    corpus = None
    def create_embedding(text):
        nonlocal corpus
        if not corpus:
            corpus = corpus_provider()
        return _tf_idf_embedding_strategy(text, corpus)
    return create_embedding

def _calculate_cosine_similarity(embedding1, embedding2):
    similarity = dot(embedding1, embedding2)/(norm(embedding1)*norm(embedding2))
    return similarity

def create_tf_idf_concept():
    strategies = []
    strategies.append({
        "id" : "corpus_default",
        "create_embedding" : _create_strategy(get_java_corpus)
    })
    strategies.append({
        "id" : "corpus_splitted_subwords",
        "create_embedding" : _create_strategy(get_java_corpus_subword)
    })
    return {
        "id" : "tf_idf",
        "strategies": strategies,
        "calculate_similarity" : _calculate_cosine_similarity
    }