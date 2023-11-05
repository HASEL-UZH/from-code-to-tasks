from src.strategies.embeddings.embedding_strategies import tf_embedding_strategy, tf_idf_embedding_strategy, \
    codebert_embedding_strategy, codebert_summed_embedding_strategy
from src.create_results import get_total_accuracy, get_statistics_object, save_results_to_csv, save_results_to_json, \
    create_pr_groups
from src.object_store import db
from src.utils.profiler import Profiler


def create_results_task():
    print("create_results_task started")
    profiler = Profiler()

# TODO add meta strategies and term strategies
    meta_strategies = []
    term_strategies = []
    # embedding_strategies = [tf_embedding_strategy, tf_idf_embedding_strategy, codebert_embedding_strategy, codebert_summed_embedding_strategy]
    embedding_strategies = [tf_embedding_strategy]
    window_sizes = [10, 20, 30]
    k_values = [1,3,5]

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
    # }

    profiler.checkpoint(f"commit foundation created - change resources: {len(change_resources)}")

    pr_groups = create_pr_groups(commit_infos)
    for window_size in window_sizes:
        if window_size > len(pr_groups):
            print(f"Windows size of {window_size} cannot be applied to to a PR dataset of size {len(pr_groups)}")
            continue

        for k in k_values:
            for embedding_strategy in embedding_strategies:
                print(f"Running results with the following parameters k = {k}, window size = {window_size}, embedding strategy = {embedding_strategy}...")
                total_accuracies = get_total_accuracy(pr_groups, k, window_size, embedding_strategy)
                if total_accuracies is None:
                    print(f"No sliding windows could be created for window size = {window_size}.")
                    continue
                statistics_object = get_statistics_object(total_accuracies)
                # save_results_to_csv(statistics_object, k, window_size, embedding_strategy)
                # save_results_to_json(statistics_object, k, window_size, embedding_strategy)
                print(f"Done running results with the following parameters k = {k}, window size = {window_size}, embedding strategy = {embedding_strategy}.")

    profiler.checkpoint(f"create_results_task done")
    db.invalidate()



if __name__=="__main__":
    create_results_task()
