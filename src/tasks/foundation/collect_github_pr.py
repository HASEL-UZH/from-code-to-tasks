from src.core.profiler import Profiler
from src.store.mdb_store import Collection
from src.tasks.foundation.collect_repositories import (
    insert_pull_requests,
    insert_issues,
)


def collect_github_pr():
    profiler = Profiler("collect_github_pr")
    repositories = Collection.github_repository.find(
        {"language": "en", "languages": None}
    ).sort("stargazerCount", -1)
    repositories = repositories[:10]
    for repository in repositories:
        repository_name = repository["name"]
        repository_owner = repository["owner"]
        insert_pull_requests(owner=repository_owner, repository_name=repository_name)
        insert_issues(owner=repository_owner, repository_name=repository_name)


if __name__ == "__main__":
    collect_github_pr()
