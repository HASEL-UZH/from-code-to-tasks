import re

from src.store.object_store import db


# TODO move function
def get_pull_requests():
    pull_requests = []
    change_resources = db.find_resources({"kind": "change", "type": "json"})
    for change_resource in change_resources:
        change_content = db.get_resource_content(change_resource, volatile=True)
        pull_requests.append(change_content["pr"]["text"])
    return pull_requests


def get_java_standard_corpus():
    corpus = []
    java_resources = db.find_resources({"type": "java", "version":"after"})
    pr_resources = get_pull_requests()
    for java_resource in java_resources:
        java_code = db.get_resource_content(java_resource)
        corpus.append(java_code)
    for pr_resource in pr_resources:
        corpus.append(pr_resource)
    return corpus


def get_java_corpus_subword():
    corpus = []
    java_resources = db.find_resources({"type": "java",  "version":"after"})
    pr_resources = get_pull_requests()
    for java_resource in java_resources:
        java_code = db.get_resource_content(java_resource)
        java_code_subword_split = subword_splitter(java_code)
        corpus.append(java_code_subword_split)
    for pr_resource in pr_resources:
        pr_subword_split = subword_splitter(pr_resource)
        corpus.append(pr_subword_split)
    return corpus


def java_corpus_standard_provider():
    corpus = None
    def create_corpus():
        nonlocal corpus
        if not corpus:
            corpus = get_java_standard_corpus()
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
