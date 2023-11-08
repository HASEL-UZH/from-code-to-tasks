from numpy import dot
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer

# TODO use shared vectorizer
def _tf_idf_embedding_strategy(text, corpus_fn):
    tf_idf_vectorizer = TfidfVectorizer()
    X = tf_idf_vectorizer.fit_transform(corpus_fn())
    shape = X.shape
    feature_names = tf_idf_vectorizer.get_feature_names_out()
    tf_idf_text_vector = tf_idf_vectorizer.transform([text]).toarray()[0]
    return tf_idf_text_vector


def _create_strategy(corpus_provider):
    def create_embedding(text):
        return _tf_idf_embedding_strategy(text, corpus_provider)
    return create_embedding

def _calculate_cosine_similarity(embedding1, embedding2):
    nominator = dot(embedding1, embedding2)
    denominator = (norm(embedding1) * norm(embedding2))
    if denominator == 0:
        pass
        return 0.0
    similarity = nominator / denominator
    return similarity


# corpus_providers: {java_corpus: ICorpusProvider, java_subword_corpus: ICorpusProvider}
def create_tf_idf_concept(corpus_providers):
    strategies = []
    strategies.append({
        "id" : "corpus_default",
        "create_embedding" : _create_strategy(corpus_providers["java_standard_corpus"])
    })
    strategies.append({
        "id" : "corpus_splitted_subwords",
        "create_embedding" : _create_strategy(corpus_providers["java_subword_corpus"])
    })
    return {
        "id" : "tf_idf",
        "strategies": strategies,
        "calculate_similarity" : _calculate_cosine_similarity
    }