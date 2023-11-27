import random
from src.calculations.create_results import get_total_accuracy, get_statistics_object
from src.core.logger import log
from src.core.profiler import Profiler
from src.github.defs import RepositoryIdentifier
from src.strategies.embeddings.codebert_concept import create_codebert_concept
from src.strategies.embeddings.codebert_summed_concept import (
    create_codebert_summed_concept,
)
from src.strategies.embeddings.tf_concept import create_tf_concept
from src.strategies.embeddings.tf_idf_concept import create_tf_idf_concept
from src.store.mdb_store import db


p = Profiler()
p.debug("ready.")
import string
import os.path

p.debug("os.path.")
import csv

p.debug("csv.")
import nltk

p.debug("nltk.")
from nltk.corpus import stopwords

p.debug("nltk.corpus.")
from nltk.tokenize import word_tokenize

p.debug("nltk.tokenize.")
import spacy

p.debug("spacy.")
import re

p.debug("re.")

from src.core.utils import (
    group_by,
    remove_cr_lf,
    truncate_string,
    split_string,
    hash_string,
)

p.debug("src.core.utils.")
from src.core.workspace_context import (
    get_store_dir,
    get_results_dir,
    write_csv_file,
    write_xlsx_file,
)

p.debug("src.core.workspace_context.")

"""
# Setup

## NLTK

```bash
pip install nltk
python -m nltk.downloader punkt stopwords
```

## SpaCy

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

"""


def nltk_model():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")


def spacy_model(model_name="en_core_web_sm"):
    try:
        # Try to load the model if it's already installed
        spacy.load(model_name)
        print(f"SpaCy model '{model_name}' is already installed.")
    except OSError:
        # If not installed, download and install the model
        print(f"SpaCy model '{model_name}' not found, downloading...")
        from spacy.cli import download

        download(model_name)
        print(f"SpaCy model '{model_name}' downloaded and installed.")


def create_analysis(items):
    results = []

    def analyze(strategy):
        p = Profiler()
        id = strategy["id"]
        technology = strategy["technology"]
        tokenization = strategy["tokenization"]

        stop_words = strategy["stop_words"]
        tokenize_fn = strategy["tokenize_fn"]
        filter_fn = strategy["filter_fn"]
        template = {
            "strategy": id,
            "technology": technology,
            "tokenization": tokenization,
            "type": "item",
            "key": None,
            "item_count": 0,
            "text_len": 0,
            "title_len": 0,
            "text_token_count": 0,
            "title_token_count": 0,
            "common_token_count": 0,
            "common_tokens": "",
            "percentage": 0,
            "title": "",
            "text": "",
        }

        tokens = []
        pr_groups = []  # does only work if we provide a single strategy

        for item in items:
            _text = " ".join(split_string(remove_cr_lf(item["change_text"])))
            _title = " ".join(split_string(remove_cr_lf(item["pull_request_text"])))
            # Tokenize and remove stop words from s_text
            text_tokens = sorted(
                [
                    w.lower()
                    for w in tokenize_fn(_text)
                    if w.lower() not in stop_words
                    and filter_fn(w)
                    and len(w.strip()) > 0
                ]
            )
            # Tokenize and remove stop words from s_title
            title_tokens = sorted(
                [
                    w.lower()
                    for w in tokenize_fn(_title)
                    if w.lower() not in stop_words
                    and filter_fn(w)
                    and len(w.strip()) > 0
                ]
            )

            text_tokens = list(set(text_tokens))
            title_tokens = list(set(title_tokens))
            tokens.extend(text_tokens + title_tokens)

            # Calculate intersection and percentage
            common_tokens = set(title_tokens).intersection(text_tokens)
            percentage = (len(common_tokens) / len(title_tokens)) if title_tokens else 0

            _title_string = truncate_string(", ".join(title_tokens))
            _text_string = truncate_string(", ".join(text_tokens))
            result = {
                **template,
                **{
                    "key": hash_string(_title),
                    "item_count": 1,
                    "commit_hash": item["commit_hash"],
                    "commit_date": item["commit_date"],
                    "title": _title_string,
                    "text": _text_string,
                    "text_len": len(_text),
                    "title_len": len(_title),
                    "text_token_count": len(text_tokens),
                    "title_token_count": len(title_tokens),
                    "common_token_count": len(common_tokens),
                    "common_tokens": ", ".join(sorted(common_tokens)),
                    "percentage": percentage,
                },
            }
            results.append(result)

            # if result["percentage"] > 0:
            # if result["percentage"]:
            if result["common_token_count"] > 1:
                # improve accuracy by removing non-matching entries
                #  compatibility format to be used for strategy based similarity analysis
                pr_groups.append(
                    {
                        "key": _title,
                        "commit_hash": item["commit_hash"],
                        "commit_date": item["commit_date"],
                        "commits": [],
                        "change_text": " ".join(text_tokens),
                        "pull_request_text": " ".join(title_tokens),
                        "common_token_count": result["percentage"],
                        "common_tokens": result["percentage"],
                        "percentage": result["percentage"],
                    }
                )
            else:
                pass
        # }

        summary_item = {
            **template,
            **{
                "key": hash_string("summary"),
                "type": "summary",
            },
        }

        # Sum up the required properties from each item in the results
        for result in results:
            summary_item["item_count"] += result["item_count"]
            summary_item["text_len"] += result["text_len"]
            summary_item["title_len"] += result["title_len"]
            summary_item["text_token_count"] += result["text_token_count"]
            summary_item["title_token_count"] += result["title_token_count"]
            summary_item["common_token_count"] += result["common_token_count"]

        # Calculate the new percentage for the summary
        # Check for division by zero just in case there are no title tokens at all
        if summary_item["title_token_count"] > 0:
            summary_item["percentage"] = (
                summary_item["common_token_count"] / summary_item["title_token_count"]
            )
        results.append(summary_item)

        # Print individual percentage for each item
        # print(f"Title: {item['s_title']} | Text: {item['s_text']} | Percentage: {percentage:.2f}%")
        p.info(f"Analysis {technology}, {id} -> {summary_item['percentage']}")
        create_results_task_local(pr_groups, tokens)  # list(set(tokens)))
        random.shuffle(pr_groups)
        create_results_task_local(pr_groups, tokens)  # list(set(tokens)))
        random.shuffle(pr_groups)
        create_results_task_local(pr_groups, tokens)  # list(set(tokens)))

    # } analyze

    exclusions = set(list(string.punctuation))

    def is_number(s):
        try:
            float(s)  # for float
        except ValueError:
            return False
        return True

    def filter_fn(s):
        # Return True if `s` is not in the exclusion set
        return s not in exclusions and not is_number(s)

    strategies = [
        {
            "id": "nltk/word_tokenize",
            "technology": "NLTK",
            "tokenization": "word_tokenize",
            "stop_words": set(stopwords.words("english")),
            "filter_fn": filter_fn,
            "tokenize_fn": word_tokenize,
        },
        # {
        #     "id": "spacy/nlp.pipe",
        #     "technology": "SpaCy",
        #     "tokenization": "nlp.pipe",
        #     "stop_words": set(),
        #     "filter_fn": filter_fn,
        #     "tokenize_fn": get_spacy_tokenizer()
        # }
    ]

    for strategy in strategies:
        analyze(strategy)

    return results


# We need no stopword filters, as the tokenizer already removed them
def get_spacy_tokenizer():
    nlp = spacy.load("en_core_web_sm")

    def tokenize(text):
        for doc in nlp.pipe([text]):
            tokens = [token.text for token in doc if not token.is_stop]
            return tokens

    return tokenize


def analyze_content_foundation():
    print("create_results_task started")

    profiler = Profiler()
    nltk_model()
    profiler.debug("nltk model ready.")

    spacy_model()
    profiler.debug("spacy model ready.")

    items = get_foundation_items()
    profiler.debug(f"commit foundation created - items: {len(items)},")

    results = create_analysis(items)
    profiler.debug(f"results: {len(items)},")

    filepath_csv = os.path.join(get_results_dir(), "foundation_analysis.csv")
    filepath_xlsx = os.path.join(get_results_dir(), "foundation_analysis.xlsx")
    write_csv_file(filepath_csv, results)
    write_xlsx_file(filepath_xlsx, results)

    profiler.info(f"create_results_task done")


def get_foundation_items():
    change_resources, commit_infos = get_resources()
    return commit_infos


def get_resources():
    change_resources = list(
        db.find_resources(
            {
                "strategy.meta": "ast-lg",
                "kind": "term",
                "type": "text",
                "strategy.terms": "meta_ast_text",
                "repository_identifier": RepositoryIdentifier.vavr_io__vavr,
            }
        )
    )
    commit_infos = []
    for change_resource in change_resources:
        change_content = db.get_resource_content(change_resource, volatile=True)
        commit = db.find_object(change_resource.get("@container"))
        change_text = change_content
        change_text = change_text.strip() if change_content else ""
        pull_request_text = (
            commit.get("pull_request_title", "")
            + " "
            + commit.get("pull_request_text", "")
        )

        commit_info = {
            "commit_hash": commit.get("commit_hash"),
            "commit_date": commit.get("commit_date"),
            "pull_request_text": pull_request_text,
            "change_text": change_text,
        }
        if change_text:
            commit_infos.append(commit_info)
    return change_resources, commit_infos


def create_items(commit_infos):
    sorted_commits = sorted(commit_infos, key=lambda x: x["commit_date"])
    groups = group_by(sorted_commits, "pull_request_text")
    items = []

    for key, values in groups.items():
        item = {
            "key": key,
            "commits": values,
            "text": ", ".join([item["change_text"] for item in values]),
            "title": key,
        }
        items.append(item)
    return items


#  pr_groups, # compatibility with existing algorithms
def create_results_task_local(pr_groups, corpus_texts):
    log.info(f"create_results_task_local started: {len(pr_groups)}")
    profiler = Profiler()

    def corpus_provider():
        return corpus_texts

    corpus_providers = {
        "corpus_standard_with_numbers": corpus_provider,
        "corpus_standard_without_numbers": corpus_provider,
    }
    embedding_concepts = [
        create_tf_concept(corpus_providers),
        create_tf_idf_concept(corpus_providers),
        # create_codebert_concept(),
        # create_codebert_summed_concept(),
    ]
    window_sizes = [10, 20, 100, 200]  # , 20, 30]
    k_values = [1]  # ,3,5]

    profiler.info(
        f"commit foundation created - change resource items: {len(pr_groups)}"
    )

    results = []
    try:
        for embedding_concept in embedding_concepts:
            embedding_strategies = embedding_concept["strategies"]
            similarity_strategy = embedding_concept["calculate_similarity"]
            for embedding_strategy in embedding_strategies:
                create_embedding = embedding_strategy["create_embedding"]
                embedding_cache = {}

                def get_embedding(text):
                    nonlocal embedding_cache
                    embedding = embedding_cache.get(text)
                    if embedding is None:
                        embedding = create_embedding(text)
                        embedding_cache[text] = embedding
                    return embedding

                for window_size in window_sizes:
                    if window_size > len(pr_groups):
                        print(
                            f"Windows size of {window_size} cannot be applied to to a PR dataset of size {len(pr_groups)}"
                        )
                        continue

                    for k in k_values:
                        result = {
                            "k": k,
                            "window_size": window_size,
                            "embeddings_concept": embedding_concept["id"],
                            "embeddings_strategy": embedding_strategy["id"],
                        }
                        print(
                            f"Running results with the following parameters {result}..."
                        )
                        context = {"errors": []}
                        total_accuracies = get_total_accuracy(
                            context,
                            pr_groups,
                            k,
                            window_size,
                            get_embedding,
                            similarity_strategy,
                        )
                        if total_accuracies:
                            statistics_object = get_statistics_object(total_accuracies)
                            result = {**result, **statistics_object}
                            results.append(result)

                        profiler.info(f"Done with the following parameters {result}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        pass
        # save_results_to_csv(results)

    profiler.info(f"create_results_task_local done")


if __name__ == "__main__":
    analyze_content_foundation()
