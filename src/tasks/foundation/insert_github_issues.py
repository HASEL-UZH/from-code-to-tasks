from src.core.logger import log
from src.store.mdb_store import Collection
from src.store.object_factory import get_repository_identifier
from src.tasks.task_01__create_repository import api


def insert_github_issues(repositories: [dict]):
    for repository in repositories:
        repository_name = repository["name"]
        repository_owner = repository["owner"]
        _insert_issues(owner=repository_owner, repository_name=repository_name)


def _insert_issues(owner: str, repository_name: str):
    result = api.get_issues(owner, repository_name, n=100, max_pages=100)
    identifier = get_repository_identifier(result["url"])
    base = {"identifier": identifier}

    entries = []
    for issue in result.get("data"):
        entry = {**base, **issue}
        entries.append(entry)

    Collection.github_issue.delete_many({"identifier": identifier})
    if entries:
        Collection.github_issue.insert_many(entries)
    log.info(f"Insert issues for {result['url']} ({len(entries)})")
