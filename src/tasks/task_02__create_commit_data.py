from src.core.profiler import Profiler
from src.core.utils import get_date_string
from src.core.workspace_context import get_file_base_name, is_java_file
from src.store.mdb_store import db, Collection
from src.store.object_factory import ObjectFactory
from src.tasks.foundation.foundation import PR_COUNT_LIMIT
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT


def create_commit_data_task(context: PipelineContext):
    repositories = list(db.find_repositories(context.create_repository_criteria()))
    profiler = Profiler("create_commit_data_task")
    for repository in repositories:
        repo_url = repository["repository_url"]
        profiler.info(f"Get commits for repository: {repo_url}")
        pr_infos = list(
            Collection.pr_info.find(
                {
                    "repository_identifier": repository.get("identifier"),
                    "accepted": True,
                }
            ).sort({"index": 1})
        )

        filtered_pr_infos = pr_infos[:PR_COUNT_LIMIT]
        Collection.commit.delete_many(context.create_commit_criteria())
        Collection.resource.delete_many(context.create_resource_criteria())
        for pr_info in filtered_pr_infos:
            save_commit_data(repository, pr_info["pr_commit"], pr_info["py_commit"])
        profiler.info(
            f"repository {repo_url} with {len(filtered_pr_infos)} of {len(pr_infos)}"
        )


def save_commit_data(repository, pr_commit, py_commit):
    commit_date = get_date_string(py_commit["commit_date"])
    seen = set()
    # code for accept first
    unique_modified_files = [
        d
        for d in (py_commit["changes"] or [])
        if d["filename"] not in seen and not seen.add(d["filename"])
    ]
    # code for accept last
    # unique_modified_files = {d.filename: d for d in (pydriller_commit.modified_files or [])}.values()
    pr_commit["merge_commit_hash"] = pr_commit.get("mergeCommit", {}).get("oid")
    commit_info = {
        "repository_url": repository["repository_url"],
        "commit_hash": py_commit["commit_hash"],
        "commit_message": py_commit["commit_message"],
        "pull_request": pr_commit,
        "pull_request_title": pr_commit.get("title"),
        "pull_request_text": pr_commit.get("bodyText"),
        "commit_author": py_commit["commit_author"],
        "commit_date": commit_date,
        "in_main_branch": py_commit["in_main_branch"],
        "merge": py_commit["merge"],
        "added_lines": py_commit["added_lines"],
        "deleted_lines": py_commit["deleted_lines"],
        "changes": [],
    }

    results = {"commit": None, "resources": []}
    commit = ObjectFactory.commit(commit_info)
    db.save_commit(commit)
    results["commit"] = commit
    commit_file_count = 0
    for py_commit_change in py_commit["changes"]:
        file_name = py_commit_change["filename"]
        base_file_name = get_file_base_name(file_name)
        if is_java_file(file_name):
            change = {
                "filename": py_commit_change["filename"],
                "change_type": py_commit_change["change_type"],
                "old_path": py_commit_change["old_path"],
                "new_path": py_commit_change["new_path"],
            }
            commit["changes"].append(change)
            if py_commit_change["modified_file_before"]:
                commit_file_count += 1
                source_before_resource = ObjectFactory.resource(
                    commit,
                    {
                        "name": base_file_name,
                        "type": "java",
                        "kind": "source",
                        "version": "before",
                        "content": py_commit_change["modified_file_before"],
                    },
                )
                db.save_resource(source_before_resource, commit)
                results["resources"].append(source_before_resource)
            if py_commit_change["modified_file_after"]:
                commit_file_count += 1
                source_after_resource = ObjectFactory.resource(
                    commit,
                    {
                        "name": base_file_name,
                        "type": "java",
                        "kind": "source",
                        "version": "after",
                        "content": py_commit_change["modified_file_after"],
                    },
                )
                db.save_resource(source_after_resource, commit)
                results["resources"].append(source_after_resource)
            if py_commit_change["modified_file_diff"]:
                commit_file_count += 1
                diff_resource = ObjectFactory.resource(
                    commit,
                    {
                        "name": base_file_name,
                        "type": "diff",
                        "kind": "diff",
                        "version": None,
                        "content": py_commit_change["modified_file_diff"],
                    },
                )
                db.save_resource(diff_resource, commit)
                results["resources"].append(diff_resource)

    db.save_commit(commit)
    return results


if __name__ == "__main__":
    # print("TASK DISABLED"); exit(0)
    create_commit_data_task(DEFAULT_PIPELINE_CONTEXT)
