import re

import requests
from pydriller import Repository

from src.workspace_context import HEADERS, FINAL_REPOSITORY_FILE, get_repository_file_path, load_json_file, \
    is_java_file, \
    write_text_file, write_json_file
from src.workspace_context import get_commit_data_file_before, get_commit_data_file_after, get_commit_data_file_diff, \
    get_commit_data_file_info


def get_commit_data(repo_infos):
    for index, repo_info in enumerate(repo_infos):
        print(f"REPOSITORY {repo_info['url']} ID: {index}")
        repository = Repository(repo_info["url"], only_modifications_with_file_types=[".java"])
        for commit in repository.traverse_commits():
            if has_pull_request(commit):
                process_commit(repo_info["url"], index, commit)
            else:
                print("PR number is None")
                continue

def process_commit(repo_url, repo_index, commit):
    pull_request_number = get_pull_request_number(commit.msg)

    try:
        print("PR number is Available")
        pull_request_url = get_pull_request_url(repo_url, pull_request_number)
        response = requests.get(pull_request_url, headers=HEADERS)
        response_json= response.json()
        if "title" in response_json:
            pull_request_title = response_json["title"]
            try:
                save_commit_data(repo_url, repo_index, commit, pull_request_title)
            except Exception as e:
                print(f"Error saving commit {commit} in {repo_url}")
        else:
            print("NOT a PR (Issue): " + str(pull_request_number))
    except Exception as e:
        print(f"An error occurred during PR fetching: {str(e)}")
def save_commit_data(repo_url, repo_index, commit, pull_request_title):
    print(pull_request_title)
    committer_date = (
        commit.author_date.date().day,
        commit.author_date.date().month,
        commit.author_date.date().year,
    )

    commit_info = {
        "repository url": repo_url,
        "commit hash": commit.hash,
        "commit message": commit.msg,
        "pull request": pull_request_title,
        "commit author": commit.author.name,
        "committer date": committer_date,
        "in main branch": commit.in_main_branch,
        "merge": commit.merge,
        "added lines": commit.insertions,
        "deleted lines": commit.deletions,
    }

    if None not in commit.modified_files:
        for modified_file in commit.modified_files:
            file_name = modified_file.filename
            if  is_java_file(file_name):
                source_code_before_path = get_commit_data_file_before(repo_index, commit.hash, file_name)
                source_code_after_path = get_commit_data_file_after(repo_index, commit.hash, file_name)
                commit_diff_path = get_commit_data_file_diff(repo_index, commit.hash, file_name)
                commit_info_path = get_commit_data_file_info(repo_index, commit.hash)

                write_text_file(source_code_before_path, modified_file.source_code_before, opts={"no_empty_file": True})
                write_text_file(source_code_after_path, modified_file.source_code, opts={"no_empty_file": True})
                write_text_file(commit_diff_path, modified_file.diff, opts={"no_empty_file": True})
        write_json_file(commit_info_path, commit_info)


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
        print(pull_request_number)
        return pull_request_number

def get_pull_request_url(repository_url, pull_request_number):
    parts = repository_url.strip("/").split("/")
    owner = parts[-2]
    repo_name = parts[-1]
    pull_request_url = (
        f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pull_request_number}"
    )
    print(pull_request_url)
    return pull_request_url

def fetch_commit_data_task():
    final_repository_file_path = get_repository_file_path(FINAL_REPOSITORY_FILE)
    final_repository_json = load_json_file(final_repository_file_path)
    final_repository_urls = final_repository_json["final_repositories"]
    get_commit_data(final_repository_urls)

if __name__ == "__main__":
    fetch_commit_data_task()
