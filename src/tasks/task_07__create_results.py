from src.calculations.create_results import (
    create_pr_groups,
    get_total_accuracy,
    get_statistics_object,
    save_results_to_csv,
)
from src.core.logger import log
from src.core.profiler import Profiler
from src.core.utils import group_by
from src.store.mdb_store import db
from src.strategies.embeddings.define_vocabulary import (
    corpus_subword_with_numbers_provider,
    corpus_subword_without_numbers_provider,
    corpus_standard_with_numbers_provider,
    corpus_standard_without_numbers_provider,
)
from src.strategies.embeddings.tf_concept import create_tf_concept
from src.strategies.embeddings.tf_idf_concept import create_tf_idf_concept


# FIXME use iterator
def get_commit_infos() -> [dict]:
    change_resources = db.find_resources({"kind": "term"})
    commit_infos = []
    for change_resource in change_resources:
        commit = db.find_object(change_resource.get("@container"))
        change_text = db.get_resource_content(change_resource)
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
    ]
    # , create_codebert_concept(), create_codebert_summed_concept()]
    window_sizes = [10]  # , 20, 30]
    k_values = [1]  # ,3,5]

    commit_infos = get_commit_infos()
    profiler.checkpoint(
        f"commit foundation created - change resources: {len(commit_infos)}"
    )

    results = []
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

                    def commit_group_key_fn(d):
                        return "::".join(
                            [
                                d.get("resource")
                                .get("strategy")
                                .get("meta", "undefined")
                                or "none",
                                d.get("resource")
                                .get("strategy")
                                .get("terms", "undefined")
                                or "none",
                            ]
                        )

                    commit_info_groups = group_by(commit_infos, commit_group_key_fn)
                    for strategy_key, commit_group in commit_info_groups.items():
                        parts = strategy_key.split("::")
                        local_result = result.copy()
                        local_result["meta_strategy"] = parts[0]
                        local_result["term_strategy"] = parts[1]
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
