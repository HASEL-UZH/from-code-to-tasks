from datetime import datetime
from typing import List
import requests
from pydriller import Repository
import json
import os
import re


def get_repositories(n):
    url = "https://api.github.com/search/repositories"
    params = {
        "q": "language:java",
        "sort": "stars",
        "order": "desc",
        "per_page": n
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        repositories = response.json()["items"]
        repo_urls = [repo["html_url"] for repo in repositories]
        return repo_urls
    else:
        return []


def get_commit_data(repo_urls: List[str]):
    for repo_url in repo_urls:
        repository = Repository(repo_url,
                                only_no_merge=True,
                                only_modifications_with_file_types=['.java'], since=datetime(2023, 6, 6, 7))
        for commit in repository.traverse_commits():
            commit_msg = commit.msg
            issue_number = get_issue_number(commit_msg)
            if issue_number is None:
                continue
            else:
                issue_url = get_issue_request_url(repo_url, issue_number)
                github_token = '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'
                headers = {"Authorization": f"token {github_token}"}
                response = requests.get(issue_url, headers=headers)
                if "title" in response.json():
                    issue_title = response.json()["title"]
                else:
                    continue

                folder_name = os.path.join('data', f'commit_{commit.hash}')
                os.makedirs(folder_name, exist_ok=True)

                commit_info = {
                    'msg': commit.msg,
                    'issue': issue_title
                }

                commit_info_path = os.path.join(folder_name, 'commit_info.json')
                with open(commit_info_path, 'w') as commit_info_file:
                    json.dump(commit_info, commit_info_file, indent=4)

                for modified_file in commit.modified_files:
                    commit_diff = modified_file.diff
                    commit_diff_path = os.path.join(folder_name, f'{commit.hash}.diff')
                    with open(commit_diff_path, 'w') as commit_diff_file:
                        commit_diff_file.write(commit_diff)


def get_issue_number(commit_msg):
    pattern = r'#(\d+)'
    issue_numbers = re.findall(pattern, commit_msg)
    if len(issue_numbers) != 1:
        return None
    else:
        issue_number = issue_numbers[0]
        return issue_number


def get_issue_request_url(repository_url, issue_number):
    parts = repository_url.strip("/").split("/")
    owner = parts[-2]
    repo_name = parts[-1]
    issue_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}"
    return issue_url

def main():
    # TODO remove

    repository_urls = ["https://github.com/EssentialsX/Essentials"]

    # TODO add

    # number_of_repositories = 2
    # repository_urls = get_repositories(number_of_repositories)

    get_commit_data(repository_urls)


if __name__ == "__main__":
    main()
