from pydriller import Repository

from src.core.logger import log
from src.core.profiler import Profiler
from src.core.utils import get_date_string
from src.core.workspace_context import (
    is_java_file,
)
from src.store.mdb_store import Collection


def insert_pydriller_commit(repositories: [dict]):
    profiler = Profiler("insert_pydriller_commit")
    for i, repository in enumerate(repositories):
        log.info(
            f"Insert github pr - {i}/{len(repositories)} current repository: {repository['identifier']}"
        )
        exists = (
            Collection.pydriller_commit.find_one(
                {"repository_identifier": repository["identifier"]}
            )
            is not None
        )
        if exists:
            profiler.info(f"Repository already exists: {repository['identifier']}")
            continue
        repo_url = repository["url"]
        profiler.info(
            f"Get pydriller commits for repository: {repository['identifier']}"
        )
        git_repository = Repository(
            repo_url, only_modifications_with_file_types=[".java"]
        )
        pydriller_commits = []
        for commit in git_repository.traverse_commits():
            profiler.debug(f"Repository data available - {repo_url}")
            pydriller_commit = _create_pydriller_commit(repository, commit)
            pydriller_commits.append(pydriller_commit)

        if pydriller_commits:
            infos = []
            infos.append({"repository": repository["identifier"]})
            for pydriller_commit in pydriller_commits:
                infos.append(
                    {
                        "commit_hash": pydriller_commit["commit_hash"],
                        "added_lines": pydriller_commit["added_lines"],
                        "deleted_lines": pydriller_commit["deleted_lines"],
                        "changes": len(pydriller_commit["changes"]),
                    }
                )
            Collection.pydriller_commit.insert_many(pydriller_commits)


def _create_pydriller_commit(repository, pydriller_commit):
    commit_date = get_date_string(pydriller_commit.author_date.date())
    seen = set()
    unique_modified_files = [
        d
        for d in (pydriller_commit.modified_files or [])
        if d.filename not in seen and not seen.add(d.filename)
    ]
    commit_info = {
        "repository_url": repository["url"],
        "repository_identifier": repository["identifier"],
        "repository_owner": repository["owner"],
        "repository_name": repository["name"],
        "commit_hash": pydriller_commit.hash,
        "commit_message": pydriller_commit.msg,
        "commit_author": pydriller_commit.author.name,
        "commit_date": commit_date,
        "in_main_branch": pydriller_commit.in_main_branch,
        "merge": pydriller_commit.merge,
        "added_lines": pydriller_commit.insertions,
        "deleted_lines": pydriller_commit.deletions,
        "changes": [],
    }

    for modified_file in unique_modified_files:
        file_name = modified_file.filename
        if is_java_file(file_name):
            change = {
                "filename": modified_file.filename,
                "change_type": modified_file.change_type.name,
                "old_path": modified_file.old_path,
                "new_path": modified_file.new_path,
                "modified_file_before": modified_file.source_code_before,
                "modified_file_after": modified_file.source_code,
                "modified_file_diff": modified_file.diff,
            }
            commit_info["changes"].append(change)

    return commit_info
