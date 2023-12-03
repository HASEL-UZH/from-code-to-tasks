from pydriller import Repository

from src.core.profiler import Profiler
from src.store.mdb_store import Collection
from src.tasks.foundation.select_repositories import create_pydriller_commit


def collect_pydriller_commit():
    profiler = Profiler("collect_pydriller_commit")
    repositories = Collection.github_repository.find(
        {"language": "en", "languages": None}
    ).sort("stargazerCount", -1)
    repositories = repositories[:10]
    for repository in repositories:
        exists = (
            Collection.pydriller_commit.find_one({"repository_url": repository["url"]})
            is not None
        )
        if exists:
            profiler.info(f"Repository already exists: {repository['url']}")
            continue
        repo_url = repository["url"]
        profiler.info(f"Get pydriller commits for repository: {repo_url}")
        git_repository = Repository(
            repo_url, only_modifications_with_file_types=[".java"]
        )
        pydriller_commits = []
        for commit in git_repository.traverse_commits():
            profiler.debug(f"Repository data available - {repo_url}")
            pydriller_commit = create_pydriller_commit(repository, commit)
            pydriller_commits.append(pydriller_commit)
        Collection.pydriller_commit.delete_many(
            {"repository_identifier": repository["url"]}
        )
        Collection.pydriller_commit.insert_many(pydriller_commits)


if __name__ == "__main__":
    collect_pydriller_commit()
