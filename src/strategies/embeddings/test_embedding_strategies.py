import re

import torch
import torch.nn.functional as F
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


def tf_embedding():
    corpus = ['The sky is blue.','The sun is bright.']
    text = 'The sun sun blue blue nightblue in the sky is bright'
    countvectorizer = CountVectorizer()
    terms = countvectorizer.fit_transform(corpus)
    shape = terms.shape
    feature_names = countvectorizer.get_feature_names_out()
    tf_text_vector = countvectorizer.transform([text]).toarray()[0]
    return tf_text_vector

def tf_idf_embedding():
    corpus = ['The sky.','The sun']
    test = 'The sun in the sky is bright'
    tfidfvectorizer = TfidfVectorizer()
    terms = tfidfvectorizer.fit_transform(corpus)
    shape = terms.shape
    feature_names = tfidfvectorizer.get_feature_names_out()
    tf_idf_text_vector = tfidfvectorizer.transform([test]).toarray()[0]
    return tf_idf_text_vector

# uses only words i.e. ; { i ignored. which is good
def tf_idf_code():
    is_prime_java_code = """
    public static boolean isPrime(int num) {
    if (num <= 1) {
        return false;
    }
    for (int i = 2; i <= Math.sqrt(num); i++) {
        if (num % i == 0) {
            return false;
        }
    }
    return true;
}
"""
    factorial_java_code = """
    public static int factorial(int n) {
        if (n == 0 || n == 1) {
            return 1;
        } else {
            int result = 1;
            for (int i = 2; i <= n; i++) {
                result *= i;
            }
            return result;
        }
    }
    """
    corpus = [is_prime_java_code, factorial_java_code]
    test = 'for (int i = 2; i <= n; i++)'
    tfidfvectorizer = TfidfVectorizer()
    terms = tfidfvectorizer.fit_transform(corpus)
    shape = terms.shape
    feature_names = tfidfvectorizer.get_feature_names_out()
    tf_idf_text_vector = tfidfvectorizer.transform([test]).toarray()[0]
    return tf_idf_text_vector


def tf_idf_embedding_subword():
    corpus = ['The howdieCo myBooleanVariable hello_world.','return false']
    new_corpus = []
    for doc in corpus:
        new_corpus.append(subword_splitter(doc))
    test = 'Added boolean variable'
    tfidfvectorizer = TfidfVectorizer()  # This includes unigrams, bigrams, and trigrams
    terms = tfidfvectorizer.fit_transform(new_corpus)
    shape = terms.shape
    feature_names = tfidfvectorizer.get_feature_names_out()
    tf_idf_text_vector = tfidfvectorizer.transform([test]).toarray()[0]
    return tf_idf_text_vector

# splits camelCase and nake_case words into subwords
def subword_splitter(input_string):
    words = re.findall(r'[A-Za-z]+', input_string)
    transformed_words = []
    for word in words:
        if '_' in word:
            subwords = word.split('_')
            transformed_words.extend(subwords)
        else:
            subwords = re.findall(r'[a-z]+|[A-Z][a-z]*', word)
            transformed_words.extend(subwords)
    output_string = ' '.join(transformed_words)
    return output_string

def test_cs_cb():
    tensor1 = torch.randn(225, 768)
    tensor2 = torch.randn(225, 768)


    similarity = F.cosine_similarity(tensor1, tensor2, dim=1)
    return similarity



if __name__ == "__main__":
    pass
    #tf_embedding()
    #tf_idf_embedding()
    #tf_idf_code()
    #tf_idf_subwords()
    test_cs_cb()

