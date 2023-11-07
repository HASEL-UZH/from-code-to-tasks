from src.create_results import get_total_accuracy, get_statistics_object, create_pr_groups, save_dict_to_csv, \
    save_dict_to_json
from src.object_store import db
from src.strategies.embeddings.tf_concept import create_tf_concept
from src.strategies.embeddings.tf_idf_concept import create_tf_idf_concept
from src.utils.profiler import Profiler


def get_resources():
    change_resources = db.find_resources({"kind": "change", "type": "json"})
    commit_infos = []
    for change_resource in change_resources:
        change_content = db.get_resource_content(change_resource, volatile=True)
        commit = db.find_object(change_resource.get("@container"))
        change_text = change_content["code"]["text"]
        change_text = change_text.strip() if change_content else ""
        commit_info = {
            "commit_hash": commit.get("commit_hash"),
            "commit_date": commit.get("commit_date"),
            "pull_request_text": change_content["pr"]["text"],
            "change_text": change_text,
            "commit_message_text": commit.get("commit_message"),
        }
        if change_text:
            commit_infos.append(commit_info)
    return change_resources, commit_infos

# TODO add meta strategies and term strategies
def create_results_task():
    print("create_results_task started")
    profiler = Profiler()

    embedding_concepts = [create_tf_concept(), create_tf_idf_concept()]
    window_sizes = [10, 20, 30]
    k_values = [1,3,5]

    change_resources, commit_infos = get_resources()
    pr_groups = create_pr_groups(commit_infos)
    profiler.checkpoint(f"commit foundation created - change resources: {len(change_resources)}, pr groups: {len(pr_groups)}")

    results = []
    for window_size in window_sizes:
        if window_size > len(pr_groups):
            print(f"Windows size of {window_size} cannot be applied to to a PR dataset of size {len(pr_groups)}")
            continue

        for k in k_values:
            for embedding_concept in embedding_concepts:
                embedding_strategies = embedding_concept["strategies"]
                similarity_strategy = embedding_concept["calculate_similarity"]
                for embedding_strategy in embedding_strategies:
                    result = {
                        "k" : k,
                        "window_size" : window_size,
                        "embeddings_concept" : embedding_concept["id"],
                        "embeddings_strategy" : embedding_strategy["id"]
                    }
                    print(f"Running results with the following parameters {result}...")
                    total_accuracies = get_total_accuracy(pr_groups, k, window_size, embedding_strategy["create_embedding"], similarity_strategy)
                    if total_accuracies:
                        statistics_object = get_statistics_object(total_accuracies)
                        result = {**result, **statistics_object}
                        results.append(result)

                    print(f"Done running results with the following parameters k = {k}, window size = {window_size}, embedding strategy = {embedding_strategy}.")
                    approach_name = f"{result['embeddings_concept']}_{result['embeddings_strategy']}_{k}_{window_size}"
                    save_dict_to_csv(result)
                    save_dict_to_json(approach_name, result)
    profiler.checkpoint(f"create_results_task done")
    db.invalidate()


if __name__=="__main__":
    create_results_task()
