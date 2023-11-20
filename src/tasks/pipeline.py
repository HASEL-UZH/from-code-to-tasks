from src.store.mdb_store import db
from src.tasks.task_01__create_repository import create_repository_task
from src.tasks.task_02__create_commit_data import create_commit_data_task
from src.tasks.task_03__create_ast import create_ast_task
from src.tasks.task_04__create_meta_ast import create_meta_ast_task
from src.tasks.task_05__create_change_model import change_model_creator_task
from src.tasks.task_06__create_change_repr import change_term_creator_task
from src.tasks.task_07__create_results import create_results_task


# from src.tasks.task_06__create_change_repr import change_term_creator_task


def run_pipeline():
    # resources = db.find_resources()
    # db.delete_resources(resources)

    # 01
    # create_repository_task()

    # 02
    # create_commit_data_task()

    # 03
    # create_ast_task()

    # 04
    # create_meta_ast_task()

    # 05
    # change_model_creator_task()

    # 06
    # change_term_creator_task()

    # 07
    create_results_task()
    pass


if __name__ == "__main__":
    # print("PIPELINE DISABLED"); exit(0)

    # create_commit_data_task(15)
    run_pipeline()
