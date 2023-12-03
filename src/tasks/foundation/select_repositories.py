from pydriller import Repository

from src.core.profiler import Profiler
from src.core.utils import get_date_string
from src.core.workspace_context import get_file_base_name, is_java_file
from src.store.mdb_store import Collection


def select_repositories():
    profiler = Profiler("select_repositories")
    repositories = Collection.github_repository.find(
        {"language": "en", "languages": None}
    ).sort("stargazerCount", -1)

    # repositories = [
    #     d for d in repositories if d["url"] == "https://github.com/vavr-io/vavr"
    # ]

    for repository in repositories:
        exists = (
            Collection.pydriller_commit.find_one({"repository_url": repository["url"]})
            is not None
        )
        if exists:
            profiler.info(f"Repository already exists: {repository['url']}")
            continue
        repo_url = repository["url"]
        profiler.info(f"Get commits for repository: {repo_url}")
        # FIXME ensure the PRs
        prs = list(
            Collection.github_pr.find({"identifier": repository.get("identifier")})
        )
        pr_commits = {
            d.get("mergeCommit").get("oid"): d for d in prs if d.get("mergeCommit")
        }
        git_repository = Repository(
            repo_url, only_modifications_with_file_types=[".java"]
        )
        match_count = 0
        mismatch_count = 0
        profiler.debug(f"Start fetching data from Pydriller - {repo_url}")
        pydriller_commits = []
        for commit in git_repository.traverse_commits():
            profiler.debug(f"Repository data available - {repo_url}")
            pydriller_commit = create_pydriller_commit(repository, commit)
            pydriller_commits.append(pydriller_commit)

        Collection.pydriller_commit.delete_many(
            {"repository_identifier": repository["url"]}
        )
        Collection.pydriller_commit.insert_many(pydriller_commits)

        profiler.info(
            f"  match: {match_count}, mismatch: {mismatch_count}, total: {match_count+mismatch_count}, PR count: {len(prs)}, with merge commit: {len(pr_commits)}"
        )


def create_pydriller_commit(repository, pydriller_commit):
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

    commit_file_count = 0
    for modified_file in unique_modified_files:
        file_name = modified_file.filename
        base_file_name = get_file_base_name(file_name)
        if is_java_file(file_name):
            change = {
                "filename": modified_file.filename,
                "change_type": modified_file.change_type.name,
                "old_path": modified_file.old_path,
                "new_path": modified_file.new_path,
                "modified_file_before": not not modified_file.source_code_before,
                "modified_file_after": not not modified_file.source_code,
                "modified_file_diff": not not modified_file.diff,
            }
            commit_info["changes"].append(change)

    return commit_info


# }


if __name__ == "__main__":
    # print("TASK DISABLED"); exit(0)
    select_repositories()
    pass
