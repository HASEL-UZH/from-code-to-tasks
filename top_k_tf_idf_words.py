from sklearn.feature_extraction.text import TfidfVectorizer

from src.strategies.embeddings.define_vocabulary import get_java_corpus


def get_top_k_tf_idf_words(k, input_text):

    vectorizer = TfidfVectorizer()
    training_data = get_java_corpus()

    # Fit the vectorizer on the training data to ensure consistent preprocessing
    vectorizer.fit(training_data)

    # Transform the input text into TF-IDF vectors
    input_vector = vectorizer.transform([input_text])

    # Extract feature names (words) from the vectorizer
    feature_names = vectorizer.get_feature_names_out()

    # Get the TF-IDF values for the input text
    tfidf_values = input_vector.toarray()[0]

    # Create a list of (word, TF-IDF) tuples and sort by TF-IDF in descending order
    sorted_tfidf = sorted(zip(feature_names, tfidf_values), key=lambda x: x[1], reverse=True)

    # Get the top k words with the highest TF-IDF values
    top_k_words = [word for word, tfidf in sorted_tfidf[:k]]

    return top_k_words