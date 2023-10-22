from sklearn.feature_extraction.text import CountVectorizer

def tf_vectorization(texts):
    count_vectorizer = CountVectorizer()
    term_frequency_matrix = count_vectorizer.fit_transform(texts)
    print(term_frequency_matrix)
    feature_names = count_vectorizer.get_feature_names_out()
    print(feature_names)
    term_frequency_matrix_array = term_frequency_matrix.toarray()
    print(term_frequency_matrix_array[0])

if __name__ == "__main__":
    texts = [
        "This is the first document.",
        "This document is the second document.",
        "And this is the third one.",
        "Is this the first document?",
    ]
tf_vectorization(texts)



