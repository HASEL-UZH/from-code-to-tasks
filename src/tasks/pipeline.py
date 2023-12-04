from src.core.logger import log
from src.github.defs import RepositoryIdentifier
from src.tasks.foundation.foundation import get_top_repositories
from src.tasks.pipeline_context import PipelineContext
from src.tasks.task_01__create_repository import create_repository_task
from src.tasks.task_02__create_commit_data import create_commit_data_task


def run_pipeline(repository_identifier):
    context = PipelineContext(
        opts={
            "repositories": [repository_identifier],
            "log_accuracy_flag": False,
        }
    )
    log.info(f"Pipeline: {context.get_opts()}")

    # db.delete_resources_where(context.create_resource_criteria())

    # 01
    create_repository_task(context)

    # 02
    create_commit_data_task(context)

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
    # Requirement: Run foundation.py

    repository_identifiers = get_top_repositories()
    repository_identifiers = [RepositoryIdentifier.iluwatar__java_design_patterns]
    for repository_identifier in repository_identifiers:
        run_pipeline(repository_identifier)

    log.info("Done.")
