from src.core.logger import log
from src.store.mdb_store import db
from src.tasks.foundation.foundation import get_top_repositories
from src.tasks.pipeline_context import PipelineContext
from src.tasks.task_01__create_repository import create_repository_task
from src.tasks.task_02__create_commit_data import create_commit_data_task
from src.tasks.task_03__create_ast import create_ast_task
from src.tasks.task_04__create_meta_ast import create_meta_ast_task
from src.tasks.task_05__create_change_model import change_model_creator_task
from src.tasks.task_06__create_change_repr import change_term_creator_task
from src.tasks.task_07__create_results import create_results_task


def run_pipeline(repository_identifier):
    context = PipelineContext(
        opts={
            "repositories": [repository_identifier],
            "log_accuracy_flag": False,
        }
    )
    log.info(f"Pipeline: {context.get_opts()}")

    db.delete_resources_where(context.create_resource_criteria())

    # 01
    create_repository_task(context)

    # 02
    create_commit_data_task(context)

    # 03
    create_ast_task(context)

    # 04
    create_meta_ast_task(context)

    # 05
    change_model_creator_task(context)

    # 06
    change_term_creator_task(context)

    # 07
    create_results_task(context)
    pass


if __name__ == "__main__":
    # Requirement: Run foundation.py

    repository_identifiers = get_top_repositories()

    for repository_identifier in repository_identifiers:
        run_pipeline(repository_identifier)

    log.info("Done.")
