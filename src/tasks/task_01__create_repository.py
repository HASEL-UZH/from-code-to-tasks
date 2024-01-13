from src.github.github_grapghql_api import github_graphql_api
from src.store.mdb_store import db, Collection
from src.store.object_factory import ObjectFactory
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT

api = github_graphql_api


def create_repository_task(context: PipelineContext):
    db.delete_repositories(context.create_repository_criteria())
    repositories = Collection.github_repository.find(
        context.create_db_filter_criteria("identifier")
    )
    for repository in repositories:
        repository_object = ObjectFactory.repository(repository["url"], repository)
        db.save_repository(repository_object)


if __name__ == "__main__":
    create_repository_task(DEFAULT_PIPELINE_CONTEXT)
