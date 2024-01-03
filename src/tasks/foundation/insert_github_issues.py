from src.core.logger import log
from src.core.profiler import Profiler
from src.github.github_grapghql_api import github_graphql_api
from src.store.mdb_store import Collection
from src.store.object_factory import get_repository_identifier

api = github_graphql_api


def insert_github_issues(repositories: [dict]):
    profiler = Profiler("insert_github_issues")
    for i, repository in enumerate(repositories):
        log.info(
            f"Insert github pr - {i}/{len(repositories)} current repository: {repository['identifier']}"
        )
        exists = (
            Collection.github_issue.find_one({"identifier": repository["identifier"]})
            is not None
        )
        print(exists)
        if exists:
            profiler.info(f"Repository already exists: {repository['url']}")
            continue
        repository_name = repository["name"]
        repository_owner = repository["owner"]
        _insert_issues(api, owner=repository_owner, repository_name=repository_name)


def _insert_issues(owner: str, repository_name: str):
    result = api.get_issues(owner, repository_name, n=100, max_pages=100)
    identifier = get_repository_identifier(result["url"])
    base = {"identifier": identifier}

    entries = []
    for issue in result.get("data"):
        entry = {**base, **issue}
        entries.append(entry)

    if entries:
        Collection.github_issue.insert_many(entries)
    log.info(f"Insert issues for {result['url']} ({len(entries)})")
