from sklearn.feature_extraction.text import TfidfVectorizer

def tf_idf_vectorization(texts):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    print(tfidf_matrix)
    feature_names = tfidf_vectorizer.get_feature_names_out()
    print(feature_names)
    tfidf_matrix_array = tfidf_matrix.toarray()
    print(tfidf_matrix_array[0])

if __name__ == "__main__":
    texts = [
        "This is the first document.",
        "This document is the second document.",
        "And this is the third one.",
        "Is this the first document?",
    ]
tf_idf_vectorization(texts)



