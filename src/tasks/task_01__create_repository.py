from src.core.logger import log
from src.core.profiler import Profiler
from src.github.defs import RepositoryIdentifier
from src.store.object_factory import ObjectFactory, Classifier
from src.store.mdb_store import db, Collection
from src.store.mdb_store import db, Collection
from src.github.github_grapghql_api import github_graphql_api
from src.store.object_factory import get_repository_identifier
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT

api = github_graphql_api


def create_repository_task(context: PipelineContext):
    # Remove existing repository objects in the database
    db.delete_repositories(context.create_repository_criteria())

    repositories = get_top_repositories(context)
    for repository in repositories:
        repository_object = ObjectFactory.repository(repository["url"], repository)
        db.save_repository(repository_object)


def get_top_repositories(context: PipelineContext):
    criteria = {
        "language": "en",
        "languages": None,
    }
    match = context.create_repository_criteria(criteria)
    pipeline = [
        {"$match": match},
        # {
        #     "$project": {
        #         "identifier": 1,
        #         "owner": 1,  # "$owner.login",  # Reshape the owner field
        #         "name": 1,
        #         "url": 1,
        #         "createdAt": 1,
        #         "updatedAt": 1,
        #         "diskUsage": 1,
        #         "forkCount": 1,
        #         "stargazerCount": 1,
        #         "stargazerCountPercent": 1,
        #     }
        # },
        {"$sort": {"stargazerCount": -1}},  # Sort by stargazerCount in descending order
        {"$limit": 9},  # Limit to the first 10 documents
    ]
    dc = Collection.github_repository.aggregate(pipeline)
    documents = list(dc)
    return documents


def get_pull_requests(owner: str, repository_name):
    profiler = Profiler()
    log.debug(f"get_pull_requests: owner: {owner}, name: {repository_name}")
    result = api.get_pull_requests(owner, repository_name, n=100, max_pages=100)
    identifier = get_repository_identifier(result["url"])
    base = {"identifier": identifier}

    entries = []
    for pr in result.get("data"):
        entry = {**base, **pr["node"]}
        commits = entry.get("commits", {}).get("edges", [])
        commits = [d.get("node", {}).get("commit") for d in commits]
        entry["commits"] = commits
        entries.append(entry)

    profiler.debug(
        f"get_pull_requests: owner: {owner}, name: {repository_name}, count: {len(entries)}"
    )
    return entries


if __name__ == "__main__":
    # print("TASK DISABLED"); exit(0)
    create_repository_task(DEFAULT_PIPELINE_CONTEXT)
