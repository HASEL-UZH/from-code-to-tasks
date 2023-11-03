from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

def tf_embedding_strategy(text):
    vectorizer = CountVectorizer()
    # TODO fix training_data
    training_data = ["your", "training", "data", "function", "class"]
    vectorizer.fit(training_data)
    tf_text_vector = vectorizer.transform([text]).toarray()[0]
    return tf_text_vector

def tf_idf_embedding_strategy(text):
    vectorizer = TfidfVectorizer()
    # TODO fix training_data
    training_data = ["your", "training", "data", "function", "class"]
    vectorizer.fit(training_data)
    tf_idf_text_vector = vectorizer.transform([text]).toarray()[0]
    return tf_idf_text_vector

# TODO CodeBERT embedding strategy
def codebert_embedding_strategy(text):
    pass
