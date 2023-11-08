import re

from src.store.object_store import db


def get_corpus_standard_with_numbers():
    corpus = []
    change_text_resources = db.find_resources({"kind":"change"})
    pr_resources = get_pull_requests()
    for change_text_resource in change_text_resources:
        change_text = db.get_resource_content(change_text_resource)["code"]["text"]
        corpus.append(change_text)
    for pr_resource in pr_resources:
        corpus.append(pr_resource)
    return corpus

def get_corpus_standard_without_numbers():
    corpus = []
    change_text_resources = db.find_resources({"kind":"change"})
    pr_resources = get_pull_requests()
    for change_text_resource in change_text_resources:
        change_text = db.get_resource_content(change_text_resource)["code"]["text"]
        corpus.append(change_text)
    for pr_resource in pr_resources:
        corpus.append(pr_resource)
    return remove_numbers(corpus)

def get_corpus_subword_with_numbers():
    corpus = []
    change_text_resources = db.find_resources({"kind":"change"})
    pr_resources = get_pull_requests()
    for change_text_resource in change_text_resources:
        change_text = db.get_resource_content(change_text_resource)["code"]["text"]
        change_text_subword_split = subword_splitter(change_text)
        corpus.append(change_text_subword_split)
    for pr_resource in pr_resources:
        pr_subword_split = subword_splitter(pr_resource)
        corpus.append(pr_subword_split)
    return corpus

def get_corpus_subword_without_numbers():
    corpus = []
    change_text_resources = db.find_resources({"kind":"change"})
    pr_resources = get_pull_requests()
    for change_text_resource in change_text_resources:
        change_text = db.get_resource_content(change_text_resource)["code"]["text"]
        change_text_subword_split = subword_splitter(change_text)
        corpus.append(change_text_subword_split)
    for pr_resource in pr_resources:
        pr_subword_split = subword_splitter(pr_resource)
        corpus.append(pr_subword_split)
    return remove_numbers(corpus)




def corpus_standard_with_numbers_provider():
    corpus = None
    def create_corpus():
        nonlocal corpus
        if not corpus:
            corpus = get_corpus_standard_with_numbers()
        return corpus
    return create_corpus

def corpus_standard_without_numbers_provider():
    corpus = None
    def create_corpus():
        nonlocal corpus
        if not corpus:
            corpus = get_corpus_standard_without_numbers()
        return corpus
    return create_corpus


def corpus_subword_with_numbers_provider():
    corpus = None
    def create_corpus():
        nonlocal corpus
        if not corpus:
            corpus = get_corpus_subword_with_numbers()
        return corpus
    return create_corpus

def corpus_subword_without_numbers_provider():
    corpus = None
    def create_corpus():
        nonlocal corpus
        if not corpus:
            corpus = get_corpus_subword_without_numbers()
        return corpus
    return create_corpus


# TODO move function
def get_pull_requests():
    pull_requests = []
    change_resources = db.find_resources({"kind": "change", "type": "json"})
    for change_resource in change_resources:
        change_content = db.get_resource_content(change_resource, volatile=True)
        pull_requests.append(change_content["pr"]["text"])
    return pull_requests


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

def remove_numbers(documents):
    pattern = r'\d+'
    regex = re.compile(pattern)
    cleaned_documents = []
    for document in documents:
        cleaned_document = regex.sub('', document)
        cleaned_documents.append(cleaned_document)
    return cleaned_documents

if __name__ == "__main__":
    get_standard_change_text_pr_corpus()