from src.create_results import get_total_accuracy, get_statistics_object, save_results_to_csv
from src.embeddings.embedding_strategies import tf_embedding_strategy, tf_idf_embedding_strategy
from src.repository_manager import get_repository_change_commits


def run_results_task():
    # TODO add meta strategies and term strategies
    meta_strategies = []
    term_strategies = []
    # TODO add codebert embedding strategy
    embedding_strategies = [tf_embedding_strategy, tf_idf_embedding_strategy]
    window_sizes = [10, 20, 30]
    k_values = [1,3,5]

    change_commits = get_repository_change_commits()
    for k in k_values:
        for window_size in window_sizes:
            for embedding_strategy in embedding_strategies:
                print(f"Running results with the following parameters k = {k}, window size = {window_size}, embedding strategy = {embedding_strategy}...")
                total_accuracies = get_total_accuracy(change_commits, k, window_size, embedding_strategy)
                statistics_object = get_statistics_object(total_accuracies)
                save_results_to_csv(statistics_object, k, window_size, embedding_strategy)
                save_results_to_json(statistics_object, k, window_size, embedding_strategy)
                print(f"Done running results with the following parameters k = {k}, window size = {window_size}, embedding strategy = {embedding_strategy}.")




if __name__=="__main__":
    run_results_task()
