import statistics

from src.strategies.defs import ICommitInfo
from src.strategies.embeddings.defs import IEmbeddingStrategy
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
        embedding_strategy: IEmbeddingStrategy,
    ):
        accuracies_over_all_windows = []
        sliding_window_index = 0
        for sliding_window in SlidingWindowProvider(commit_infos, window_size):
            accuracy_per_window = self.get_accuracy_per_window(
                sliding_window_index,
                sliding_window,
                k,
                embedding_strategy,
            )
            accuracies_over_all_windows.append(accuracy_per_window)
            sliding_window_index += 1
        return accuracies_over_all_windows

    def get_accuracy_per_window(
        self,
        sliding_window_index: int,
        sliding_window: [ICommitInfo],
        k: int,
        embedding_strategy: IEmbeddingStrategy,
    ):
        correct_predictions = 0
        sliding_window_items = {d["commit_hash"]: d for d in sliding_window}

        item_pr_change_comparison = {}

        for commit_info in sliding_window:
            item_text_commit_hash = commit_info["commit_hash"]
            item_change_text = commit_info["change_text"]
            item_change_text_embedding = embedding_strategy.get_embedding(
                item_change_text
            )
            for item_pr in sliding_window:
                item_pr_commit_hash = item_pr["commit_hash"]
                item_pull_request_text = item_pr["pull_request_text"]
                item_pull_request_embedding = embedding_strategy.get_embedding(
                    item_pull_request_text
                )
                try:
                    similarity = embedding_strategy.calculate_similarity(
                        item_change_text_embedding, item_pull_request_embedding
                    )
                    item_pr_change_comparison[item_pr_commit_hash] = similarity
                except Exception as e:
                    _data = {"k": k}
                    self._context.error(
                        scope="get_accuracy_per_window", message=str(e), data=_data
                    )

            top_keys = sorted(
                item_pr_change_comparison,
                key=item_pr_change_comparison.get,
                reverse=True,
            )
            top_k_keys = top_keys[:k]

            match = item_text_commit_hash in top_k_keys
            if match:
                correct_predictions += 1
            else:
                pass

            self._context.log_accuracy(
                item_pr,
                sliding_window_index,
                sliding_window_items,
                match=match,
                accuracies=item_pr_change_comparison,
                top_keys=top_keys,
            )

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
