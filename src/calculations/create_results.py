import csv
import os
import statistics
from datetime import datetime

from src.core.utils import group_by
from src.core.workspace_context import get_results_dir
from src.store.mdb_store import Collection
from src.tasks.pipeline_context import PipelineContext


def get_total_accuracy(
    context, commit_infos, k, window_size, embedding_strategy, similarity_strategy=None
):
    sliding_windows = create_sliding_windows(commit_infos, window_size)
    if not sliding_windows:
        return None
    accuracies_over_all_windows = []
    for sliding_window in sliding_windows:
        accuracy_per_window = get_accuracy_per_window(
            context, sliding_window, k, embedding_strategy, similarity_strategy
        )
        accuracies_over_all_windows.append(accuracy_per_window)
    return accuracies_over_all_windows


def get_accuracy_per_window(
    context: PipelineContext,
    sliding_window,
    k,
    embedding_strategy,
    similarity_strategy=None,
):
    correct_predictions = 0
    for item_text in sliding_window["items"]:
        item_text_commit = item_text["commit_hash"]
        item_text_change_comparison = {}
        item_change_text = item_text["change_text"]
        item_change_text_embedding = embedding_strategy(item_change_text)
        for item_pr in sliding_window["items"]:
            item__pr_commit = item_pr["commit_hash"]
            item_pull_request_text = item_pr["pull_request_text"]
            item_pull_request_embedding = embedding_strategy(item_pull_request_text)

            try:
                similarity = similarity_strategy(
                    item_change_text_embedding, item_pull_request_embedding
                )
                item_text_change_comparison[item__pr_commit] = similarity
            except Exception as e:
                _data = {"k": k}
                context.error(
                    scope="get_accuracy_per_window", message=str(e), data=_data
                )

        top_k_keys = sorted(
            item_text_change_comparison,
            key=item_text_change_comparison.get,
            reverse=True,
        )[:k]

        if item_text_commit in top_k_keys:
            correct_predictions += 1
    accuracy_per_window = correct_predictions / sliding_window["window_size"]
    return accuracy_per_window


def create_pr_groups(commit_infos):
    sorted_commits = sorted(commit_infos, key=lambda x: x["commit_date"])
    groups = group_by(sorted_commits, "pull_request_text")
    pr_groups = []

    for key, values in groups.items():
        item = {
            "key": key,
            "commits": values,
            "change_text": ", ".join([item["change_text"] for item in values]),
            "pull_request_text": key,
        }
        pr_groups.append(item)
    return pr_groups


def create_sliding_windows(commit_infos, window_size):
    sliding_windows = []
    window_count = max(0, len(commit_infos) - window_size)
    for i in range(window_count):
        sw_items = commit_infos[i : i + window_size]
        sliding_window = {
            "window_size": window_size,
            "items": sw_items,
        }
        sliding_windows.append(sliding_window)
    return sliding_windows


def get_statistics_object(accuracies_over_all_windows):
    mean_value = statistics.mean(accuracies_over_all_windows)
    median_value = statistics.median(accuracies_over_all_windows)
    stdev_value = (
        statistics.stdev(accuracies_over_all_windows)
        if len(accuracies_over_all_windows) >= 2
        else None
    )
    min_value = min(accuracies_over_all_windows)
    max_value = max(accuracies_over_all_windows)
    statistics_object = {
        "mean": mean_value,
        "median": median_value,
        "stdev": stdev_value,
        "min": min_value,
        "max": max_value,
    }
    return statistics_object


def save_results_to_csv(results):
    if not results:
        return
    results_dir_path = get_results_dir()
    results_file_path = os.path.join(results_dir_path, "results.csv")
    headers = list(results[0].keys())
    with open(results_file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


def save_results_to_db(context, results):
    repository_identifiers = context.get_repository_identifiers()
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    results = [
        {
            "date": formatted_date,
            "repository_identifiers": repository_identifiers[0],
            **result,
        }
        for result in results
    ]
    Collection.results.insert_many(results)
