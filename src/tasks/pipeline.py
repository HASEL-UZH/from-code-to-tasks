from src.core.logger import log
from src.github.defs import RepositoryIdentifier
from src.tasks.foundation.collect_repositories import insert_pull_requests
from src.tasks.pipeline_context import PipelineContext


def run_pipeline():
    context = PipelineContext(
        opts={
            # "repositories": [RepositoryIdentifier.iluwatar__java_design_patterns],
            "repositories": [RepositoryIdentifier.vavr_io__vavr],
            "log_accuracy_flag": False,
        }
    )
    insert_pull_requests(owner="vavr-io", repository_name="vavr")

    log.info(f"Pipeline: {context.get_opts()}")
    # update_pull_requests_with_issue_information(context)

    # db.delete_resources_where(context.create_resource_criteria())

    # 01
    # create_repository_task(context)

    # 02
    # create_commit_data_task(context)

    # 03
    # create_ast_task(context)

    # 04
    # create_meta_ast_task(context)

    # 05
    # change_model_creator_task(context)

    # 06
    # change_term_creator_task(context)

    # 07
    # create_results_task(context)
    pass


if __name__ == "__main__":
    # print("PIPELINE DISABLED"); exit(0)

    # create_commit_data_task(15)
    run_pipeline()
