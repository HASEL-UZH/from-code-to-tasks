from typing import List
import requests
from pydriller import Repository
import json
import os
import re

github_token = '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'
headers = {'Authorization': f'Bearer {github_token}'}

def get_commit_data(repo_urls: List[str]):
    for repo_url in repo_urls:
        repository = Repository(repo_url, only_modifications_with_file_types=['.java'])
        for commit in repository.traverse_commits():
            commit_hash = commit.hash
            commit_msg = commit.msg
            commit_author = commit.author.name
            committer_date = commit.author_date.date().day , commit.author_date.date().month , commit.author_date.date().year ,
            in_main_branch = commit.in_main_branch
            merge = commit.merge
            insertions = commit.insertions
            deletions = commit.deletions
            pull_request_number = get_pull_request_number(commit_msg)
            if pull_request_number is None:
                print('pull request number is none')
                continue
            else:
                print('pull request number is NOT none')
                pull_request_url = get_pull_request_url(repo_url, pull_request_number)
                response = requests.get(pull_request_url, headers=headers)
                if "title" in response.json():
                    pull_request_title = response.json()["title"]
                    print(pull_request_title)
                else:
                    print('NOT A PR: ' + str(pull_request_number))
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
                        'repository url' : repo_url,
                        'commit hash': commit_hash,
                        'commit message' : commit_msg,
                        'pull request': pull_request_title,
                        'commit author' : commit_author,
                        'committer date' : committer_date,
                        'in main branch' : in_main_branch,
                        'merge' : merge,
                        'added lines' : insertions,
                        'deleted lines' : deletions,
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

def get_pull_request_number(commit_msg):
    pattern = r'#(\d+)'
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
    pull_request_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pull_request_number}"
    print(pull_request_url)
    return pull_request_url


def main():
    repository_urls = ["https://github.com/iluwatar/java-design-patterns",
                       "https://github.com/spring-projects/spring-framework",
                       "https://github.com/NationalSecurityAgency/ghidra",
                       "https://github.com/square/retrofit",
                       "https://github.com/bumptech/glide",
                       "https://github.com/SeleniumHQ/selenium",
                       "https://github.com/TeamNewPipe/NewPipe",
                       "https://github.com/apache/skywalking",
                       "https://github.com/libgdx/libgdx",
                       "https://github.com/mybatis/mybatis-3"]
    get_commit_data(repository_urls)

if __name__ == "__main__":
    main()
