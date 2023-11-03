import torch
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from transformers import AutoModel, AutoTokenizer

from src.object_store import db

model = AutoModel.from_pretrained("microsoft/codebert-base")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

def get_java_corpus():
    corpus = []
    resources = db.get_resources()
    java_resources = [obj for obj in resources if obj["type"] == "java"]
    for java_resource in java_resources:
        java_code = db.load_resource(java_resource)
        words = word_tokenize(java_code)
        corpus.extend(words)
    return corpus

# Returns a single vector as NP array
def tf_embedding_strategy(text):
    vectorizer = CountVectorizer()
    # TODO fix training_data
    training_data = get_java_corpus()
    vectorizer.fit(training_data)
    tf_text_vector = vectorizer.transform([text]).toarray()[0]
    return tf_text_vector

# Returns a single vector as NP array
def tf_idf_embedding_strategy(text):
    vectorizer = TfidfVectorizer()
    # TODO fix training_data
    training_data = get_java_corpus()
    vectorizer.fit(training_data)
    tf_idf_text_vector = vectorizer.transform([text]).toarray()[0]
    return tf_idf_text_vector


    # Separate NL from PL like this:
    # tokens=[tokenizer.cls_token]+nl_tokens+[tokenizer.sep_token]+code_tokens+[tokenizer.eos_token]
    # Returns torch object of dimension 3
def codebert_embedding_strategy(text):
    text_tokens = tokenizer.tokenize(text)
    number_of_tokens = len(text_tokens)
    if len(text_tokens)> 510:
        raise Exception(f"CodeBERT input is too large. Maximum token limit of 510 is exceeded. Number of tokens inputted are {number_of_tokens}")
    tokens = [tokenizer.cls_token]+text_tokens+[tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    embeddings = model(torch.tensor(tokens_ids)[None,:])[0]
    return embeddings

    # Returns torch object of dimension 2
def codebert_summed_embedding_strategy(text):
    text_tokens = tokenizer.tokenize(text)
    number_of_tokens = len(text_tokens)
    if len(text_tokens)> 510:
        raise Exception(f"CodeBERT input is too large. Maximum token limit of 510 is exceeded. Number of tokens inputted are {number_of_tokens}")
    tokens = [tokenizer.cls_token]+text_tokens+[tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    embeddings = model(torch.tensor(tokens_ids)[None,:])[0]
    summed_embeddings = torch.sum(embeddings, dim=1)
    return summed_embeddings


# if __name__ == "__main__":
#     text = "hello code my variable x = 5 for i in x call my function"
#     embedding_not_summed = codebert_embedding_strategy(text)
#     print(embedding_not_summed.shape)
#     torch.Size([1, 15, 768])
#     embedding_summed = codebert_summed_embedding_strategy(text)
#     print(embedding_summed.shape)
#     torch.Size([1, 768])
