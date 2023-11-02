import numpy as np

from src.repository_manager import get_repository_change_commits
from src.utils.utils import group_by


def get_total_accuracy(commits, window_size, str):
    sliding_windows = create_sliding_windows(commits, window_size)
    for sliding_window in sliding_windows:
        get_accuracy_per_window(sliding_window)

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
            "change text" : ', '.join ( [item["change_text"] for item in values]),
            "pull_request_text": key,
        }
        items.append(item)
    #     for commit in group
    window_count = len(items)-window_size
    for i in range(window_count):
        sw_items = items[i:i+window_size]
        sliding_window = {
            "window_size": window_size,
            "items" : sw_items,

        }
        sliding_windows.append(sliding_window)
    return sliding_windows

def get_accuracy_per_window(window_commits):
    pass

# There are multiple ways to generate embeddings (TF, TF-iDF, CodeBERT)
def generate_embedding(text):
    pass

def calculate_cosine_similarity(embedding1, embedding2):
    cosine_similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    return cosine_similarity

def tf_idf_embedding_strategy():
    pass

def result_creator_task():
    change_commits = get_repository_change_commits()
    window_size = 10
    get_total_accuracy(change_commits, window_size, tf_idf_embedding_strategy())
    # Evaluation metrics: mean, median, min, max, stdev

if __name__=="__main__":
    result_creator_task()
