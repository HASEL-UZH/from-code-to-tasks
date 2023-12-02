from src.calculations.acurracy_calculator import AccuracyCalculator
from src.calculations.create_results import (
    get_statistics_object,
    save_results_to_csv,
)
from src.core.logger import log
from src.core.profiler import Profiler
from src.core.workspace_context import get_results_file, write_text_file
from src.strategies.change_content_provider import ChangeContentProvider
from src.strategies.embeddings.codebert_summed_concept import CodeBertSummedConcept
from src.strategies.embeddings.tf_concept import TfConcept
from src.strategies.embeddings.tf_idf_concept import TfIdfConcept
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT


def create_results_task(context: PipelineContext):
    print("create_results_task started")
    profiler = Profiler()

    # embedding_concepts = [TfConcept(), TfIdfConcept()]
    embedding_concepts = [CodeBertSummedConcept()]

    window_sizes = [10]  # , 20, 30]
    k_values = [1]  # ,3,5]

    profiler.info(f"commit foundation created")

    results = []
    accuracy_calculator = AccuracyCalculator(context)
    for embedding_concept in embedding_concepts:
        for embedding_strategy in embedding_concept.embedding_strategies:
            for content_strategy in embedding_concept.content_strategies:
                content_provider = ChangeContentProvider()
                commit_infos = content_provider.get_content(context, content_strategy)

                if isinstance(embedding_concept, TfConcept) or isinstance(
                    embedding_concept, TfIdfConcept
                ):
                    corpus_texts = []
                    for commit_info in commit_infos:
                        corpus_texts.append(commit_info["pull_request_text"])
                        corpus_texts.append(commit_info["change_text"])

                    corpus_feature_names = embedding_strategy.init(
                        corpus_texts
                    ).tolist()
                    if corpus_feature_names:
                        corpus_filename = f"corpus_{embedding_concept.name}-{embedding_strategy.name}--{content_strategy['meta']}-{content_strategy['terms']}.text"
                        corpus_filepath = get_results_file(corpus_filename)
                        write_text_file(
                            corpus_filepath, "\n".join(corpus_feature_names)
                        )

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

                        context.set_scope(
                            {
                                "embedding_concept": embedding_concept,
                                "embedding_strategy": embedding_strategy,
                                "content_strategy": content_strategy,
                                "window_size": window_size,
                                "k": k,
                            }
                        )
                        total_accuracies = accuracy_calculator.get_total_accuracy(
                            commit_infos,
                            k,
                            window_size,
                            embedding_strategy,
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
