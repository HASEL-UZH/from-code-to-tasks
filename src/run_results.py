import csv
import os
import random

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

import statistics
from src.repository_manager import get_repository_change_commits
from src.utils.utils import group_by
from src.workspace_context import get_results_dir


def get_total_accuracy(commits, window_size, embedding_strategy, k):
    sliding_windows = create_sliding_windows(commits, window_size)
    accuracies_over_all_windows = []
    for sliding_window in sliding_windows:
        accuracy_per_window = get_accuracy_per_window(sliding_window, embedding_strategy, k)
        accuracies_over_all_windows.append(accuracy_per_window)
    return accuracies_over_all_windows

# Repository specific and repository unspecific
# interface ISlidingWindow
# {'key': 'Fix typos spanish readme and factory', 'commits': [{'commit_date': '', 'repo_id': '0', 'commit_hash': '0ad44ced247191cc631100010ca40b4baa84d161', 'pull_request_text': 'Fix typos spanish readme and factory', 'change_text': 'jldfjlljfdjlfdjlfa'}, {'commit_date': '', 'repo_id': '0', 'commit_hash': '0398509823409580324580845', 'pull_request_text': 'Fix typos spanish readme and factory', 'change_text': 'sdfsdfasdfsdfsadfsafsdfsdfsdfasff'}], 'change text': 'jldfjlljfdjlfdjlfa, sdfsdfasdfsdfsadfsafsdfsdfsdfasff', 'pull_request_text': 'Fix typos spanish readme and factory'}

def create_sliding_windows(commits, window_size):
    sliding_windows = []
    sorted_commits = sorted(commits, key=lambda x: x["commit_date"])
    groups = group_by(sorted_commits, 'pull_request_text')
    items = []

    for key, values in groups.items():
        item = {
            "key": key,
            "commits": values,
            "change_text" : ', '.join ( [item["change_text"] for item in values]),
            "pull_request_text": key,
        }
        items.append(item)
    window_count = len(items)-window_size
    for i in range(window_count):
        sw_items = items[i:i+window_size]
        sliding_window = {
            "window_size": window_size,
            "items" : sw_items,
        }
        sliding_windows.append(sliding_window)
    return sliding_windows

def get_accuracy_per_window(sliding_window, embedding_strategy, k):
    correct_predictions = 0
    for item_code in sliding_window["items"]:
        item_code_change_comparison = {}
        item_change_text = item_code["change_text"]
        item_change_text_embedding = embedding_strategy(item_change_text)
        for item_pr in sliding_window["items"]:
            item_pull_request_text = item_pr["pull_request_text"]
            item_pull_request_embedding = embedding_strategy(item_pull_request_text)
            similarity = calculate_cosine_similarity(item_change_text_embedding, item_pull_request_embedding)
            item_code_change_comparison[item_pr["key"]] = similarity
        top_k_keys = sorted(item_code_change_comparison, key=item_code_change_comparison.get, reverse=True)[:k]
        if item_code["pull_request_text"] in top_k_keys:
            correct_predictions+=1
    accuracy_per_window = correct_predictions/sliding_window["window_size"]
    return accuracy_per_window

# Embedding Strategies
def tf_embedding_strategy(text):
    vectorizer = CountVectorizer()
    # TODO fix training_data
    training_data = ["your", "training", "data", "function", "class"]
    vectorizer.fit(training_data)
    tf_text_vector = vectorizer.transform([text]).toarray()[0]
    return tf_text_vector

def tf_idf_embedding_strategy(text):
    vectorizer = TfidfVectorizer()
    # TODO fix training_data
    training_data = ["your", "training", "data", "function", "class"]
    vectorizer.fit(training_data)
    tf_idf_text_vector = vectorizer.transform([text]).toarray()[0]
    return tf_idf_text_vector

# TODO CodeBERT embedding strategy


# Similarity Calculation
def calculate_cosine_similarity(embedding1, embedding2):
    #cosine_similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    # TODO remove
    cosine_similarity = random.random()
    return cosine_similarity

def get_statistics_object(accuracies_over_all_windows):
    mean_value = statistics.mean(accuracies_over_all_windows)
    median_value = statistics.median(accuracies_over_all_windows)
    stdev_value = statistics.stdev(accuracies_over_all_windows)
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


def save_results_to_csv(statistics_object, title, k, window_size):
    results_dir_path = get_results_dir()
    results_file_path = os.path.join(results_dir_path, "results.csv")

    file_exists = os.path.exists(results_file_path)

    with open(results_file_path, mode='a', newline='') as file:
        fieldnames = ['title', 'k', 'window_size', 'mean', 'median', 'min', 'max', 'stdev']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # If the file doesn't exist, write the headers
        if not file_exists:
            writer.writeheader()

        # Write the statistics to the CSV file
        writer.writerow({
            'title': title,
            'k': k,
            'window_size': window_size,
            'mean': statistics_object['mean'],
            'median': statistics_object['median'],
            'min': statistics_object['min'],
            'max': statistics_object['max'],
            'stdev': statistics_object['stdev']
        })


def result_creator_task():
    change_commits = get_repository_change_commits()
    title = "xyz"
    k=5
    window_size = 10
    total_accuracies = get_total_accuracy(change_commits, window_size, tf_embedding_strategy, k)
    statistics_object = get_statistics_object(total_accuracies)
    save_results_to_csv(statistics_object, title, k, window_size)

if __name__=="__main__":
    result_creator_task()
