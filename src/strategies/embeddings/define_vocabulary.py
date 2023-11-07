import re

from src.object_store import db


def get_java_corpus():
    print("get regular corpus")
    corpus = []
    resources = db.get_resources()
    java_resources = [obj for obj in resources if obj["type"] == "java"]
    for java_resource in java_resources:
        java_code = db.get_resource_content(java_resource)
        corpus.append(java_code)
    return corpus

def get_java_corpus_subword():
    print("get subword corpus")
    corpus = []
    resources = db.get_resources()
    java_resources = [obj for obj in resources if obj["type"] == "java"]
    for java_resource in java_resources:
        java_code = db.get_resource_content(java_resource)
        java_code_subword_splitted = subword_splitter(java_code)
        corpus.append(java_code_subword_splitted)
    return corpus

def java_corpus_standard_provider():
    corpus = None
    def create_corpus():
        nonlocal corpus
        if not corpus:
            corpus = get_java_corpus()
        return corpus
    return create_corpus

def java_corpus_subword_provider():
    corpus = None
    def create_corpus():
        nonlocal corpus
        if not corpus:
            corpus = get_java_corpus_subword()
        return corpus
    return create_corpus

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
