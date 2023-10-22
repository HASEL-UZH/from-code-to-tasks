from typing import List
import requests
from pydriller import Repository
import json
import os
import re

github_token = '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'
headers = {'Authorization': f'Bearer {github_token}'}

statistics_object = {
    "0": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "1": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "2": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "3": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "4": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "5": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "6": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "7": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "8": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
    "9": {"no_number": 0, "number_of_issues": 0, "number_of_prs": 0, "number_of_commits": 0},
}

def get_commit_data(repo_urls: List[str]):
    for index, repo_url in enumerate(repo_urls):
        print(f"REPOSITORY {repo_url} ID: {index}")
        repository = Repository(repo_url, only_modifications_with_file_types=['.java'])
        for commit in repository.traverse_commits():
            statistics_maker(str(index), "number_of_commits")
            # Commit Info
            commit_hash = commit.hash
            commit_msg = commit.msg
            commit_author = commit.author.name
            committer_date = commit.author_date.date().day , commit.author_date.date().month , commit.author_date.date().year ,
            in_main_branch = commit.in_main_branch
            merge = commit.merge
            insertions = commit.insertions
            deletions = commit.deletions
            # Get PR number
            pull_request_number = get_pull_request_number(commit_msg)
            # Continue if PR number is None
            if pull_request_number is None:
                statistics_maker(str(index), "no_number")
                print('PR number is None')
                continue
            else:
                # Fetch PR from number
                try:
                    print('PR number is Available')
                    pull_request_url = get_pull_request_url(repo_url, pull_request_number)
                    response = requests.get(pull_request_url, headers=headers)
                    if "title" in response.json():
                        pull_request_title = response.json()["title"]
                        print(pull_request_title)
                        statistics_maker(str(index), "number_of_prs")
                    else:
                        print('NOT a PR (Issue): ' + str(pull_request_number))
                        statistics_maker(str(index), "number_of_issues")
                        continue
                except Exception as e:
                    print(f"An error occurred during PR fetching: {str(e)}")
                    continue

                # Define Folder
                folder_name = os.path.join('../commit_data', f'commit_{index}_{commit.hash}')
                os.makedirs(folder_name, exist_ok=True)
                # Define Commit Info
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

                try:
                    if None not in commit.modified_files:
                        for modified_file in commit.modified_files:
                            file_name = modified_file.filename
                            if not file_name.endswith(".java"):
                                continue
                            # Can be None if file is deleted or only renamed
                            source_code_before = modified_file.source_code_before
                            # Can be None if file is added or only renamed
                            source_code_after = modified_file.source_code
                            commit_diff = modified_file.diff

                            source_code_before_path = os.path.join(folder_name, f'{file_name}_before')
                            with open(source_code_before_path, 'w') as source_code_before_file:
                                source_code_before_file.write(source_code_before)

                            source_code_after_path = os.path.join(folder_name, f'{file_name}_after')
                            with open(source_code_after_path, 'w') as source_code_after_file:
                                source_code_after_file.write(source_code_after)

                            commit_diff_path = os.path.join(folder_name, f'{file_name}.diff')
                            with open(commit_diff_path, 'w') as commit_diff_file:
                                commit_diff_file.write(commit_diff)

                            commit_info_path = os.path.join(folder_name, 'commit_info.json')
                            with open(commit_info_path, 'w') as commit_info_file:
                                json.dump(commit_info, commit_info_file, indent=4)
                except Exception as e:
                    print(f"An error occurred during file operations: {str(e)}")


def statistics_maker(key, value):
    global statistics_object
    if key in statistics_object and value in statistics_object[key]:
        # Increment the corresponding value
        statistics_object[key][value] += 1
    else:
        print("Invalid key or value. Cannot update statistics.")

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
                       "https://github.com/mybatis/mybatis-3"
                       ]
    get_commit_data(repository_urls)
    print(json.dumps(statistics_object, indent=4))

if __name__ == "__main__":
    main()
