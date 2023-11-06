import re

import nltk
import torch

nltk.download("punkt")

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from transformers import AutoModel, AutoTokenizer

from src.object_store import db

model = AutoModel.from_pretrained("microsoft/codebert-base")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

def get_java_corpus():
    corpus = []
    resources = db.get_resources()
    java_resources = [obj for obj in resources if obj["type"] == "java"]
    for java_resource in java_resources:
        java_code = db.get_resource_content(java_resource)
        corpus.append(java_code)
    return corpus

# TODO add
def get_java_corpus_subword():
    corpus = []
    resources = db.get_resources()
    java_resources = [obj for obj in resources if obj["type"] == "java"]
    for java_resource in java_resources:
        java_code = db.get_resource_content(java_resource)
        java_code_subword_splitted = subword_splitter(java_code)
        corpus.append(java_code_subword_splitted)
    return corpus

def tf_embedding_strategy(text):
    count_vectorizer = CountVectorizer()
    corpus = get_java_corpus()
    X = count_vectorizer.fit_transform(corpus)
    shape = X.shape
    feature_names = count_vectorizer.get_feature_names_out()
    tf_text_vector = count_vectorizer.transform([text]).toarray()[0]
    return tf_text_vector

def tf_idf_embedding_strategy(text):
    tf_idf_vectorizer = TfidfVectorizer()
    corpus = get_java_corpus()
    X = tf_idf_vectorizer.fit_transform(corpus)
    shape = X.shape
    feature_names = tf_idf_vectorizer.get_feature_names_out()
    tf_idf_text_vector = tf_idf_vectorizer.transform([text]).toarray()[0]
    return tf_idf_text_vector


    # Separate NL from PL like this:
    # tokens=[tokenizer.cls_token]+nl_tokens+[tokenizer.sep_token]+code_tokens+[tokenizer.eos_token]
    # Returns torch object of dimension 3
def codebert_embedding_strategy(text):
    text_tokens = tokenizer.tokenize(text)
    number_of_tokens = len(text_tokens)
    if len(text_tokens)> 510:
        pass
        #raise Exception(f"CodeBERT input is too large. Maximum token limit of 510 is exceeded. Number of tokens inputted are {number_of_tokens}")
    tokens = [tokenizer.cls_token]+text_tokens+[tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    embeddings = model(torch.tensor(tokens_ids)[None,:])[0]
    return embeddings

    # Returns torch object of dimension 2
def codebert_summed_embedding_strategy(text):
    text_tokens = tokenizer.tokenize(text)
    number_of_tokens = len(text_tokens)
    if len(text_tokens)> 510:
        pass
        #raise Exception(f"CodeBERT input is too large. Maximum token limit of 510 is exceeded. Number of tokens inputted are {number_of_tokens}")
    tokens = [tokenizer.cls_token]+text_tokens+[tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    embeddings = model(torch.tensor(tokens_ids)[None,:])[0]
    summed_embeddings = torch.sum(embeddings, dim=1)
    return summed_embeddings

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


# if __name__ == "__main__":
#     text = "hello code my variable x = 5 for i in x call my function"
#     embedding_not_summed = codebert_embedding_strategy(text)
#     print(embedding_not_summed.shape)
#     torch.Size([1, 15, 768])
#     embedding_summed = codebert_summed_embedding_strategy(text)
#     print(embedding_summed.shape)
#     torch.Size([1, 768])
