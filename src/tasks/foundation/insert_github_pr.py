from src.core.logger import log
from src.core.profiler import Profiler
from src.github.github_grapghql_api import github_graphql_api
from src.store.mdb_store import Collection
from src.store.object_factory import get_repository_identifier


def insert_github_pr(repositories: [dict]):
    profiler = Profiler("insert_github_pr")
    for i, repository in enumerate(repositories):
        log.info(
            f"Insert github pr - {i}/{len(repositories)} current repository: {repository.get('identifier')}"
        )
        exists = (
            Collection.github_pr.find_one({"identifier": repository["identifier"]})
            is not None
        )
        if exists:
            profiler.info(
                f"Repository already exists: {repository['url']} in github pr collection"
            )
            continue
        repository_name = repository["name"]
        repository_owner = repository["owner"]
        _insert_pull_requests(owner=repository_owner, repository_name=repository_name)


def _insert_pull_requests(owner: str, repository_name: str):
    result = github_graphql_api.get_pull_requests(
        owner, repository_name, n=100, max_pages=100
    )
    identifier = get_repository_identifier(result["url"])
    base = {"identifier": identifier}

    entries = []
    for pr in result.get("data"):
        entry = {**base, **pr["node"]}
        commits = entry.get("commits", {}).get("edges", [])
        commits = [d.get("node", {}).get("commit") for d in commits]
        entry["commits"] = commits
        entries.append(entry)
    Collection.github_pr.insert_many(entries)
