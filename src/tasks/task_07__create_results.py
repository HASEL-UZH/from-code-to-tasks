from src.calculations.acurracy_calculator import AccuracyCalculator
from src.core.profiler import Profiler
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT

from src.calculations.create_results import (
    get_statistics_object,
    save_results_to_csv,
)
from src.core.logger import log
from src.store.memory_cache import MemoryCache, Memento
from src.strategies.change_content_provider import ChangeContentProvider
from src.strategies.defs import CacheStrategy
from src.strategies.embeddings.tf_concept import TfConcept
from src.strategies.embeddings.tf_idf_concept import TfIdfConcept


def create_results_task(context: PipelineContext):
    print("create_results_task started")
    profiler = Profiler()

    embedding_concepts = [TfConcept(), TfIdfConcept()]
    embedding_concepts = [TfIdfConcept()]

    window_sizes = [10]  # , 20, 30]
    k_values = [1]  # ,3,5]

    profiler.info(f"commit foundation created")

    results = []
    for embedding_concept in embedding_concepts:
        embedding_strategy_factories = embedding_concept.embedding_strategies
        for embedding_strategy_factory in embedding_strategy_factories:
            content_strategies = embedding_concept.content_strategies
            cache_strategy = embedding_concept.cache_strategy
            for content_strategy in content_strategies:

                def get_embedding_cache():
                    # nonlocal cache_strategy
                    if cache_strategy == CacheStrategy.Memory:
                        return MemoryCache()
                    elif cache_strategy == CacheStrategy.Npy:
                        pass
                    else:
                        raise Exception

                embedding_cache = get_embedding_cache()

                content_provider = ChangeContentProvider(context, content_strategy)
                commit_infos = list(content_provider)

                def content_provider():
                    content = []
                    for commit_info in commit_infos:
                        content.append(commit_info["pull_request_text"])
                        content.append(commit_info["change_text"])
                    return content

                content = Memento(content_provider)
                embedding_strategy = (
                    embedding_strategy_factory.create_embedding_strategy(content.value)
                )

                def get_embedding(text):
                    embedding = embedding_cache.get_value(
                        text, lambda: embedding_strategy.create_embedding(text)
                    )
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
                            "embeddings_concept": embedding_concept.name,
                            "embeddings_strategy": embedding_strategy.name,
                        }
                        log.debug(
                            f"Running results with the following parameters {result}..."
                        )

                        local_result = result.copy()
                        local_result["meta_strategy"] = content_strategy["meta"]
                        local_result["term_strategy"] = content_strategy["terms"]

                        accuracy_calculator = AccuracyCalculator(context)
                        total_accuracies = accuracy_calculator.get_total_accuracy(
                            commit_infos,
                            k,
                            window_size,
                            get_embedding,
                            embedding_strategy.calculate_simularity,
                        )
                        if total_accuracies:
                            statistics_object = get_statistics_object(total_accuracies)
                            result = {**local_result, **statistics_object}
                            results.append(result)

                        profiler.info(f"Done with the following parameters {result}")

    save_results_to_csv(results)
    profiler.checkpoint(f"create_results_task done")


if __name__ == "__main__":
    create_results_task(DEFAULT_PIPELINE_CONTEXT)
