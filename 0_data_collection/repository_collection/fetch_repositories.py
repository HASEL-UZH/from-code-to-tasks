import json
import os
import requests
import time

# GitHub Personal Access Token for authentication
github_token = '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'
headers = {'Authorization': f'Bearer {github_token}'}


# Function to get the number of issues or pull requests for a repository
def get_issue_pr_number(repo_owner: str, repo_name: str, type: str) -> int:
    try:
        issue_pr_url = f"https://api.github.com/search/issues?q=repo:{repo_owner}/{repo_name}+is:{type}"
        response = requests.get(issue_pr_url, headers=headers)
        if response.status_code == 200:
            if "total_count" in response.json():
                number_of_issues_prs = response.json()["total_count"]
            else:
                return 0
        else:
            return 0
    except requests.exceptions.RequestException as e:
        return 0

    # Limiting API requests to 30 requests per minute
    time.sleep(2)
    return number_of_issues_prs


# Function to fetch the most popular Java repositories with a minimum number of issues and pull requests
def fetch_most_popular_java_repositories_with_issues(number_of_repositories, issue_minimum, pr_minimum):
    params = {
        'q': f'language:java',
        'sort': 'stars',
        'order': 'desc',
        'page': '1',
        'per_page': '200',
        'since': '2022-01-01T00:00:00Z',
        'before': '2021-01-01T00:00:00Z',
    }
    response = requests.get('https://api.github.com/search/repositories', headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        repositories = data['items']
        candidate_repositories = {"repositories": []}
        for repo in repositories:
            repo_name = repo['name']
            repo_owner = repo['owner']['login']
            issue_number = get_issue_pr_number(repo_owner, repo_name, 'issue')
            pr_number = get_issue_pr_number(repo_owner, repo_name, 'pr')

            # Check if the repository meets the minimum issue and pull request requirements
            if issue_number > issue_minimum and pr_number > pr_minimum:
                repository_url = f"https://github.com/{repo_owner}/{repo_name}"
                candidate_repositories["repositories"].append(repository_url)
                if len(candidate_repositories) == number_of_repositories:
                    break
            else:
                continue
        return candidate_repositories
    else:
        return None


if __name__ == '__main__':
    number_of_repositories = 40
    issue_minimum = 500
    pr_minimum = 500

    # Fetch the most popular Java repositories meeting the specified criteria
    repositories_final = fetch_most_popular_java_repositories_with_issues(number_of_repositories, issue_minimum,
                                                                          pr_minimum)

    # Define the output JSON file path
    json_filename = '../repositories/candidate_repositories.json'
    repository_collection_folder = 'repository_collection'
    data_collection_folder = os.path.join(repository_collection_folder, os.path.dirname(json_filename))
    os.makedirs(data_collection_folder, exist_ok=True)

    # Write the final repositories data to a JSON file
    with open(json_filename, 'w') as json_file:
        json.dump(repositories_final, json_file, indent=4)
