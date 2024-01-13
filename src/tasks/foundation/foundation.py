from src.core.utils import group_by
from src.store.mdb_store import Collection
from src.tasks.foundation.insert_github_issues import insert_github_issues
from src.tasks.foundation.insert_github_pr import insert_github_pr
from src.tasks.foundation.insert_pr_info import insert_pr_info
from src.tasks.foundation.insert_pydriller_commit import insert_pydriller_commit

PR_COUNT_LIMIT = 100


def get_top_repositories(n: int = 20, min_pr_count: int = PR_COUNT_LIMIT) -> [str]:
    pr_infos = list(
        Collection.pr_info.find({"accepted": True}).sort({"stargazer_count": -1})
    )
    pr_info_groups = group_by(pr_infos, "repository_identifier")
    repository_identifiers = []
    for repo_identifier, repo_pr_infos in pr_info_groups.items():
        if len(repo_pr_infos) >= min_pr_count:
            repository_identifiers.append(repo_identifier)
    return repository_identifiers[:n]


def collect_top_repositories(n: int = 20):
    repositories = list(
        Collection.github_repository.find(
            {
                "language": "en",
                "languages": None,
                "createdAt": {"$lte": "2022-01-01T00:00:00Z"},
                "updatedAt": {"$gte": "2023-01-01T00:00:00Z"},
                "forkCount": {"$gte": 1000},
                "diskUsage": {"$gte": 5000},
            }
        ).sort("stargazerCount", -1)
    )
    repositories = repositories[:n]
    repositories = [
        repo for repo in repositories if repo.get("identifier") in repositories
    ]

    insert_github_pr(repositories)
    insert_github_issues(repositories)
    insert_pydriller_commit(repositories)
    insert_pr_info(repositories)


if __name__ == "__main__":
    collect_top_repositories()
