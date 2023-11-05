import re

import requests
from pydriller import Repository

from src.object_factory import ObjectFactory, get_resource_id
from src.object_store import db
from src.utils.utils import get_date_string
from src.workspace_context import HEADERS, is_java_file, get_file_base_name
from src.utils.profiler import Profiler


def create_commit_data_task(limit=None):
    print("create_commit_data_task started")
    repositories = db.get_repositories()

    repository_count = 0
    commit_count = 0
    total_commit_count = 0
    profiler = Profiler()

    for repository in repositories:
        repository_count += 1
        repo_url = repository["repository_url"]
        print(f"Get commits for repository: {repo_url}")
        git_repository = Repository(repo_url, only_modifications_with_file_types=[".java"])
        for commit in git_repository.traverse_commits():
            if has_pull_request(commit):
                processed = process_commit(repository, commit)
                if processed:
                    commit_count += 1
            if commit_count % 1 == 0:
                profiler.checkpoint(f"process_commit: {commit_count}")
            total_commit_count += commit_count
            if limit and commit_count >= limit:
                break


    profiler.checkpoint(f"create_commit_data_task done: total repositories: {len(repositories)}, total commits: {total_commit_count}")
    db.invalidate()



def process_commit(repository, git_commit):
    repo_url = repository["repository_url"]
    pull_request_number = get_pull_request_number(git_commit.msg)

    processed = False
    try:
        # print("PR number is Available")
        pull_request_url = get_pull_request_url(repo_url, pull_request_number)
        response = requests.get(pull_request_url, headers=HEADERS)
        response_json = response.json()
        if "title" in response_json:
            pull_request_title = response_json["title"]
            try:
                results = save_commit_data(repository, git_commit, pull_request_title)
                processed = len(results["resources"]) > 0
            except Exception as e:
                print(f"Error saving commit {git_commit} in {repo_url}, {e}")
        else:
            # print("NOT a PR (Issue): " + str(pull_request_number))
            pass
    except Exception as e:
        print(f"An error occurred during PR fetching: {str(e)}")
    return processed


def save_commit_data(repository, git_commit, pull_request_title):
    commit_date = get_date_string(git_commit.author_date.date())

    commit_info = {
        "repository_url": repository["repository_url"],
        "commit_hash": git_commit.hash,
        "commit_message": git_commit.msg,
        "pull_request": pull_request_title,
        "commit_author": git_commit.author.name,
        "commit_date": commit_date,
        "in_main_branch": git_commit.in_main_branch,
        "merge": git_commit.merge,
        "added_lines": git_commit.insertions,
        "deleted_lines": git_commit.deletions,
    }

    results = {
        "commit": None,
        "resources": []
    }
    if None not in git_commit.modified_files:
        commit = ObjectFactory.commit(commit_info)
        db.save_commit(commit)
        results["commit"] = commit
        commit_file_count = 0
        for modified_file in git_commit.modified_files:
            file_name = modified_file.filename
            base_file_name = get_file_base_name(file_name)
            if  is_java_file(file_name):
                if modified_file.source_code_before:
                    commit_file_count += 1
                    source_before_resource = ObjectFactory.resource(commit, {
                       "name": base_file_name,
                       "type": "java",
                       "kind": "source",
                       "version": "before",
                       "content": modified_file.source_code_before
                    })
                    db.save_resource(source_before_resource, commit)
                    results["resources"].append(source_before_resource)
                if modified_file.source_code:
                    commit_file_count += 1
                    source_after_resource = ObjectFactory.resource(commit, {
                       "name": base_file_name,
                       "type": "java",
                       "kind": "source",
                       "version": "after",
                       "content": modified_file.source_code
                    })
                    db.save_resource(source_after_resource, commit)
                    results["resources"].append(source_after_resource)
                if modified_file.diff:
                    commit_file_count += 1
                    diff_resource = ObjectFactory.resource(commit, {
                       "name": base_file_name,
                       "type": "diff",
                       "kind": "diff",
                       "version": None,
                       "content": modified_file.diff
                    })
                    db.save_resource(diff_resource, commit)
                    results["resources"].append(diff_resource)
        #}
    #}
    return results
#}


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
    #print("TASK DISABLED"); exit(0)
    create_commit_data_task()
