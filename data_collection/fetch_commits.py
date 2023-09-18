from typing import List
import requests
from pydriller import Repository
import json
import os
import re

github_token = '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'


def get_commit_data(repo_urls: List[str]):
    for repo_url in repo_urls:
        repository = Repository(repo_url,
                                only_no_merge=True,
                                only_modifications_with_file_types=['.java'])
        for commit in repository.traverse_commits():
            commit_msg = commit.msg
            issue_number = get_issue_number(commit_msg)
            if issue_number is None:
                continue
            else:
                issue_url = get_issue_request_url(repo_url, issue_number)
                headers = {"Authorization": f"token {github_token}"}
                response = requests.get(issue_url, headers=headers)
                if "title" in response.json():
                    issue_title = response.json()["title"]
                else:
                    continue

                # only commits that changed only one file
                if len(commit.modified_files) != 1:
                    continue

                for modified_file in commit.modified_files:
                    if modified_file is None:
                        continue
                    file_name = modified_file.filename
                    commit_diff = modified_file.diff
                    source_code_before = modified_file.source_code_before
                    source_code_after = modified_file.source_code

                    folder_name = os.path.join('commit_data', f'commit_{commit.hash}')
                    os.makedirs(folder_name, exist_ok=True)

                    commit_info = {
                        'issue': issue_title
                    }

                    commit_info_path = os.path.join(folder_name, 'commit_info.json')
                    with open(commit_info_path, 'w') as commit_info_file:
                        json.dump(commit_info, commit_info_file, indent=4)

                    commit_diff_path = os.path.join(folder_name, f'{file_name}.diff')
                    with open(commit_diff_path, 'w') as commit_diff_file:
                        commit_diff_file.write(commit_diff)

                    source_code_before_path = os.path.join(folder_name, f'{file_name}_before.java')
                    with open(source_code_before_path, 'w') as source_code_before_file:
                        source_code_before_file.write(source_code_before)

                    source_code_after_path = os.path.join(folder_name, f'{file_name}_after.java')
                    with open(source_code_after_path, 'w') as source_code_after_file:
                        source_code_after_file.write(source_code_after)


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
    repository_urls = ["https://github.com/EssentialsX/Essentials"]
    get_commit_data(repository_urls)


if __name__ == "__main__":
    main()
