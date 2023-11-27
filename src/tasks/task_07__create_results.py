from src.calculations.create_results import (
    get_total_accuracy,
    get_statistics_object,
    save_results_to_csv,
)
from src.core.logger import log
from src.core.profiler import Profiler
from src.github.defs import RepositoryIdentifier
from src.store.mdb_store import db
from src.store.memory_cache import MemoryCache
from src.strategies.change_content_provider import get_change_content_infos
from src.strategies.embeddings.codebert_concept import create_codebert_concept
from src.strategies.embeddings.codebert_summed_concept import (
    create_codebert_summed_concept,
)
from src.strategies.embeddings.define_vocabulary import (
    corpus_subword_with_numbers_provider,
    corpus_subword_without_numbers_provider,
    corpus_standard_with_numbers_provider,
    corpus_standard_without_numbers_provider,
)
from src.strategies.embeddings.defs import CacheStrategy
from src.strategies.embeddings.tf_concept import create_tf_concept
from src.strategies.embeddings.tf_idf_concept import create_tf_idf_concept


# FIXME use iterator
def get_commit_infos() -> [dict]:
    change_resources = db.find_resources(
        {
            "strategy.meta": "ast-lg",
            "kind": "term",
            "type": "text",
            "strategy.terms": "meta_ast_text",
            "repository_identifier": RepositoryIdentifier.iluwatar__java_design_patterns,
        }
    )
    commit_infos = []
    for change_resource in change_resources:
        commit = db.find_object(change_resource.get("@container"))
        change_text = db.get_resource_content(change_resource)[0:100]
        pull_request_text = commit["pull_request_title"]
        commit_info = {
            "commit_hash": commit.get("commit_hash"),
            "commit_date": commit.get("commit_date"),
            "pull_request_text": pull_request_text,
            "change_text": change_text,
            "commit_message_text": commit.get("commit_message"),
            "filename": change_resource["filename"],
            "resource": change_resource,
        }
        if change_text:
            commit_infos.append(commit_info)
    return commit_infos


def create_results_task():
    print("create_results_task started")
    profiler = Profiler()

    corpus_providers = {
        "corpus_standard_with_numbers": corpus_standard_with_numbers_provider(),
        "corpus_standard_without_numbers": corpus_standard_without_numbers_provider(),
        "corpus_subword_with_numbers": corpus_subword_with_numbers_provider(),
        "corpus_subword_without_numbers": corpus_subword_without_numbers_provider(),
    }
    embedding_concepts = [
        create_tf_concept(corpus_providers),
        create_tf_idf_concept(corpus_providers),
        create_codebert_concept(),
        create_codebert_summed_concept(),
    ]
    embedding_concepts = [
        create_tf_concept(corpus_providers),
    ]

    window_sizes = [10]  # , 20, 30]
    k_values = [1]  # ,3,5]

    commit_infos = get_commit_infos()
    profiler.info(f"commit foundation created - change resources: {len(commit_infos)}")

    results = []
    for embedding_concept in embedding_concepts:
        embedding_strategies = embedding_concept["strategies"]
        similarity_strategy = embedding_concept["calculate_similarity"]
        for embedding_strategy in embedding_strategies:
            create_embedding = embedding_strategy["create_embedding"]

            content_strategies = embedding_concept["content_strategies"]
            cache_strategy = embedding_concept["cache_strategy"]

            for content_strategy in content_strategies:
                commit_infos = get_change_content_infos(content_strategy)

                def get_embedding_cache():
                    # nonlocal cache_strategy
                    if cache_strategy == CacheStrategy.Memory:
                        return MemoryCache()
                    elif cache_strategy == CacheStrategy.Npy:
                        pass
                    else:
                        raise Exception

                embedding_cache = get_embedding_cache()

                # def _get_embedding(text):
                #     nonlocal embedding_cache
                #     embedding = embedding_cache.get(text)
                #     if embedding is None:
                #         # provider create_embedding(text)
                #         embedding = create_embedding(text)
                #         embedding_cache[text] = embedding
                #     return embedding

                def get_embedding(text):
                    embedding = embedding_cache.get_value(
                        text, lambda: create_embedding(text)
                    )
                    return embedding

                for window_size in window_sizes:
                    if window_size > len(commit_infos):
                        log.info(
                            f"Windows size of {window_size} cannot be applied to to a PR dataset of size {len(commit_infos)}"
                        )
                        continue

                    for k in k_values:
                        result = {
                            "k": k,
                            "window_size": window_size,
                            "embeddings_concept": embedding_concept["id"],
                            "embeddings_strategy": embedding_strategy["id"],
                        }
                        log.info(
                            f"Running results with the following parameters {result}..."
                        )

                        local_result = result.copy()
                        local_result["meta_strategy"] = content_strategy["meta"]
                        local_result["term_strategy"] = content_strategy["terms"]
                        context = {"errors": []}
                        total_accuracies = get_total_accuracy(
                            context,
                            commit_infos,
                            k,
                            window_size,
                            get_embedding,
                            similarity_strategy,
                        )
                        if total_accuracies:
                            statistics_object = get_statistics_object(total_accuracies)
                            result = {**local_result, **statistics_object}
                            result["errors"] = len(context["errors"])
                            results.append(result)

                        profiler.info(f"Done with the following parameters {result}")

    save_results_to_csv(results)

    profiler.checkpoint(f"create_results_task done")


if __name__ == "__main__":
    create_results_task()
