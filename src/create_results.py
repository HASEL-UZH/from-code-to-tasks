import csv
import os

import statistics
from src.utils.utils import group_by
from src.workspace_context_old import get_results_dir


def get_total_accuracy(pr_groups, k, window_size, embedding_strategy, similarity_strategy=None):
    sliding_windows = create_sliding_windows(pr_groups, window_size)
    if not sliding_windows:
        return None
    accuracies_over_all_windows = []
    for sliding_window in sliding_windows:
        accuracy_per_window = get_accuracy_per_window(sliding_window, k, embedding_strategy, similarity_strategy)
        accuracies_over_all_windows.append(accuracy_per_window)
    return accuracies_over_all_windows


def get_accuracy_per_window(sliding_window, k, embedding_strategy, similarity_strategy=None):
    correct_predictions = 0
    for item_code in sliding_window["items"]:
        item_code_change_comparison = {}
        item_change_text = item_code["change_text"]
        item_change_text_embedding = embedding_strategy(item_change_text)
        for item_pr in sliding_window["items"]:
            item_pull_request_text = item_pr["pull_request_text"]
            item_pull_request_embedding = embedding_strategy(item_pull_request_text)
            if similarity_strategy:
                similarity = similarity_strategy(item_change_text_embedding, item_pull_request_embedding)
            item_code_change_comparison[item_pr["key"]] = similarity
        top_k_keys = sorted(item_code_change_comparison, key=item_code_change_comparison.get, reverse=True)[:k]
        if item_code["pull_request_text"] in top_k_keys:
            correct_predictions+=1
    accuracy_per_window = correct_predictions/sliding_window["window_size"]
    return accuracy_per_window

def create_pr_groups(commit_infos):
    sorted_commits = sorted(commit_infos, key=lambda x: x["commit_date"])
    groups = group_by(sorted_commits, 'pull_request_text')
    pr_groups = []

    for key, values in groups.items():
        item = {
            "key": key,
            "commits": values,
            "change_text" : ', '.join ( [item["change_text"] for item in values]),
            "pull_request_text": key,
        }
        pr_groups.append(item)
    return pr_groups


def create_sliding_windows(pr_groups, window_size):
    sliding_windows = []
    window_count = max(0, len(pr_groups)-window_size)
    for i in range(window_count):
        sw_items = pr_groups[i:i+window_size]
        sliding_window = {
            "window_size": window_size,
            "items" : sw_items,
        }
        sliding_windows.append(sliding_window)
    return sliding_windows


def get_statistics_object(accuracies_over_all_windows):
    mean_value = statistics.mean(accuracies_over_all_windows)
    median_value = statistics.median(accuracies_over_all_windows)
    stdev_value = statistics.stdev(accuracies_over_all_windows) if len(accuracies_over_all_windows) >= 2 else None
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
    with open(results_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

