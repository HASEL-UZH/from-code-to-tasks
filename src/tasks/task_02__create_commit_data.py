import re
from pydriller import Repository
from src.core.profiler import Profiler
from src.core.utils import get_date_string
from src.core.workspace_context import get_file_base_name, is_java_file
from src.store.object_factory import ObjectFactory
from src.store.mdb_store import db, Collection
from src.github.defs import RepositoryIdentifier


def create_commit_data_task():
    repositories = list(db.find_repositories())
    repositories = [
        d
        for d in repositories
        if d["identifier"] == RepositoryIdentifier.iluwatar__java_design_patterns
    ]
    profiler = Profiler("create_commit_data_task")

    match_count = 0
    mismatch_count = 0

    for repository in repositories:
        repo_url = repository["repository_url"]
        profiler.info(f"Get commits for repository: {repo_url}")
        prs = list(
            Collection.github_pr.find({"identifier": repository.get("identifier")})
        )
        pr_commits = {
            d.get("mergeCommit").get("oid"): d for d in prs if d.get("mergeCommit")
        }
        git_repository = Repository(
            repo_url, only_modifications_with_file_types=[".java"]
        )
        for commit in git_repository.traverse_commits():
            pr_commit = pr_commits.get(commit.hash)
            if pr_commit:
                profiler.info(f"PR commit found: {commit.hash}")
                save_commit_data(repository, pr_commit, commit)
                match_count += 1
            else:
                profiler.debug(f"PR commit not found: {commit.hash}")
                mismatch_count += 1
        profiler.info(
            f"  match: {match_count}, mismatch: {mismatch_count}, total: {match_count+mismatch_count}, PR count: {len(prs)}, with merge commit: {len(pr_commits)}"
        )


def save_commit_data(repository, pr_commit, pydriller_commit):
    commit_date = get_date_string(pydriller_commit.author_date.date())
    seen = set()
    # code for accept first
    unique_modified_files = [
        d
        for d in (pydriller_commit.modified_files or [])
        if d.filename not in seen and not seen.add(d.filename)
    ]
    # code for accept last
    # unique_modified_files = {d.filename: d for d in (pydriller_commit.modified_files or [])}.values()
    pr_commit["merge_commit_hash"] = pr_commit.get("mergeCommit", {}).get("oid")
    commit_info = {
        "repository_url": repository["repository_url"],
        "commit_hash": pydriller_commit.hash,
        "commit_message": pydriller_commit.msg,
        "pull_request": pr_commit,
        "pull_request_title": pr_commit.get("title"),
        "pull_request_text": pr_commit.get("bodyText"),
        "commit_author": pydriller_commit.author.name,
        "commit_date": commit_date,
        "in_main_branch": pydriller_commit.in_main_branch,
        "merge": pydriller_commit.merge,
        "added_lines": pydriller_commit.insertions,
        "deleted_lines": pydriller_commit.deletions,
        "changes": [],
    }

    results = {"commit": None, "resources": []}
    commit = ObjectFactory.commit(commit_info)
    db.save_commit(commit)
    results["commit"] = commit
    commit_file_count = 0
    for modified_file in []:  # unique_modified_files:
        file_name = modified_file.filename
        base_file_name = get_file_base_name(file_name)
        if is_java_file(file_name):
            change = {
                "filename": modified_file.filename,
                "change_type": modified_file.change_type.name,
                "old_path": modified_file.old_path,
                "new_path": modified_file.new_path,
            }
            commit["changes"].append(change)
            if modified_file.source_code_before:
                commit_file_count += 1
                source_before_resource = ObjectFactory.resource(
                    commit,
                    {
                        "name": base_file_name,
                        "type": "java",
                        "kind": "source",
                        "version": "before",
                        "content": modified_file.source_code_before,
                    },
                )
                db.save_resource(source_before_resource, commit)
                results["resources"].append(source_before_resource)
            if modified_file.source_code:
                commit_file_count += 1
                source_after_resource = ObjectFactory.resource(
                    commit,
                    {
                        "name": base_file_name,
                        "type": "java",
                        "kind": "source",
                        "version": "after",
                        "content": modified_file.source_code,
                    },
                )
                db.save_resource(source_after_resource, commit)
                results["resources"].append(source_after_resource)
            if modified_file.diff:
                commit_file_count += 1
                diff_resource = ObjectFactory.resource(
                    commit,
                    {
                        "name": base_file_name,
                        "type": "diff",
                        "kind": "diff",
                        "version": None,
                        "content": modified_file.diff,
                    },
                )
                db.save_resource(diff_resource, commit)
                results["resources"].append(diff_resource)
    # }
    db.save_commit(commit)
    # }
    return results


# }


def has_pull_request(commit):
    pull_request_number = get_pull_request_number(commit.msg)
    return pull_request_number is not None


def get_pull_request_number(commit_msg):
    pattern = r"#(\d+)"
    pull_request_numbers = re.findall(pattern, commit_msg)
    if len(pull_request_numbers) != 1:
        return None
    else:
        pull_request_number = pull_request_numbers[0]
        return pull_request_number


def get_pull_request_url(repository_url, pull_request_number):
    parts = repository_url.strip("/").split("/")
    owner = parts[-2]
    repo_name = parts[-1]
    pull_request_url = (
        f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pull_request_number}"
    )
    return pull_request_url


if __name__ == "__main__":
    # print("TASK DISABLED"); exit(0)
    create_commit_data_task()
