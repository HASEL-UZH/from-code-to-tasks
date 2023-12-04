from typing import TypedDict, Any

from src.core.profiler import Profiler
from src.core.utils import group_by
from src.store.mdb_store import Collection


class IPrInfo(TypedDict):
    pr_commit: Any
    py_commit: Any
    repository: str
    number_source_files: int
    number_unique_files: int
    number_test_files: int
    duplicate_title: bool
    number_lines: int


class IPrStatistics(TypedDict):
    pr_infos: [IPrInfo]
    src_files_max: int
    src_files_min: int
    lines_max: int
    lines_min: int


def collect_pr_info():
    profiler = Profiler("select_commits")
    repositories = Collection.github_repository.find(
        {"language": "en", "languages": None, "identifier": "vavr-io__vavr"}
    ).sort("stargazerCount", -1)
    repositories = repositories[:10]
    for repository in repositories:
        repository_identifier = repository.get("identifier")
        profiler.info(f"process repository: {repository_identifier}")
        pr_commits = list(
            Collection.github_pr.find({"identifier": repository_identifier})
        )
        # exclude PR without merge commit
        pr_commits = [d for d in pr_commits if d.get("mergeCommit")]

        py_commits = list(
            Collection.pydriller_commit.find(
                {"repository_identifier": repository.get("identifier")}
            )
        )

        pr_infos = create_pr_infos(repository, pr_commits, py_commits)
        Collection.pr_info.delete_many({"repository": repository_identifier})
        if pr_infos:
            Collection.pr_info.insert_many(pr_infos)
        profiler.info(f"process repository done: {repository_identifier}")


def create_pr_infos(repository: dict, pr_commits: [dict], py_commits: [dict]):
    pr_infos = []
    pr_title_statistics = {}
    for pr_commit in pr_commits:
        pr_title = pr_commit.get("title")
        pr_entry = pr_title_statistics.get(pr_title)
        if not pr_entry:
            pr_title_statistics[pr_title] = 0
        pr_title_statistics[pr_title] += 1
    # _pr_commits = [
    #     d for d in pr_commits if pr_title_statistics[d.get("title")] == 1
    # ]
    # _pr_commit_lookup = {d.get("mergeCommit").get("oid"): d for d in pr_commits}
    py_commit_lookup = {d["commit_hash"]: d for d in py_commits}
    for pr_commit in pr_commits:
        commit_hash = pr_commit.get("mergeCommit").get("oid")
        py_commit = py_commit_lookup.get(commit_hash)

        pr_info: IPrInfo = {
            "pr_commit": pr_commit,
            "py_commit": py_commit,
            "repository": repository["identifier"],
            "number_source_files": None,
            "number_unique_files": None,
            "number_test_files": None,
            "duplicate_title": pr_title_statistics[pr_commit.get("title")] > 1,
            "number_lines": None,
        }
        pr_infos.append(pr_info)
        if py_commit:
            # Add PyDriller info
            added_deleted_lines = py_commit["added_lines"] + py_commit["deleted_lines"]
            py_commit_changes = py_commit["changes"]
            py_commit_file_groups = group_by(py_commit_changes, "filename")
            unique_file_names = list(py_commit_file_groups.keys())

            pr_info["number_source_files"] = len(py_commit_changes)
            pr_info["number_unique_files"] = len(py_commit_file_groups)
            pr_info["number_test_files"] = len(
                [d for d in unique_file_names if "test" in d.lower()]
            )
            pr_info["number_lines"] = added_deleted_lines

        accept_info = get_accept_info(pr_info)
        pr_info.update(accept_info)

    return pr_infos


def get_accept_info(pr_info):
    if not pr_info["py_commit"]:
        return {
            "accepted": False,
            "omit_reason": "no py commit",
        }
    # Remove PRs with duplicate title
    if pr_info["duplicate_title"]:
        return {
            "accepted": False,
            "omit_reason": "duplicate title",
        }
    # # Remove PRs where majority of files are test files
    if pr_info["number_test_files"] / pr_info["number_source_files"] >= 0.5:
        return {
            "accepted": False,
            "omit_reason": "number test files",
        }
    return {
        "accepted": True,
        "omit_reason": None,
    }


if __name__ == "__main__":
    collect_pr_info()
