import statistics

from src.strategies.defs import ICommitInfo
from src.strategies.sliding_window_provider import SlidingWindowProvider
from src.tasks.pipeline_context import PipelineContext


class AccuracyCalculator:
    _context: PipelineContext

    def __init__(self, context: PipelineContext):
        self._context = context

    def get_total_accuracy(
        self,
        commit_infos: [ICommitInfo],
        k,
        window_size,
        embedding_strategy,
        similarity_strategy=None,
    ):
        accuracies_over_all_windows = []
        for sliding_window in SlidingWindowProvider(commit_infos, window_size):
            accuracy_per_window = self.get_accuracy_per_window(
                sliding_window, k, embedding_strategy, similarity_strategy
            )
            accuracies_over_all_windows.append(accuracy_per_window)
        return accuracies_over_all_windows

    def get_accuracy_per_window(
        self,
        sliding_window: [ICommitInfo],
        k,
        embedding_strategy,
        similarity_strategy=None,
    ):
        correct_predictions = 0
        for commit_info in sliding_window:
            item_text_commit = commit_info["commit_hash"]
            item_text_change_comparison = {}
            item_change_text = commit_info["change_text"]
            item_change_text_embedding = embedding_strategy(item_change_text)
            for item_pr in sliding_window:
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
                    self._context.error(
                        scope="get_accuracy_per_window", message=str(e), data=_data
                    )

            top_k_keys = sorted(
                item_text_change_comparison,
                key=item_text_change_comparison.get,
                reverse=True,
            )[:k]

            if item_text_commit in top_k_keys:
                correct_predictions += 1

        accuracy_per_window = correct_predictions / len(sliding_window)
        return accuracy_per_window

    def get_statistics_object(self, accuracies_over_all_windows):
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
