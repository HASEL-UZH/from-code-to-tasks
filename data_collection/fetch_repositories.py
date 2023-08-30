import json
import os
import requests

github_token = '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'

# issues (open and closed) excluding pull requests
def get_issue_length(repo_owner: str, repo_name: str, headers: str) -> int:
    issues = []
    page = 1
    while True:
        issues_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues?page={page}&state=all&pulls=false"
        issues_response = requests.get(issues_url, headers=headers)

        if issues_response.status_code == 200:
            issues_data = issues_response.json()
            if len(issues_data) == 0:
                break
            issues.extend(issues_data)
            page += 1
        else:
            print(f"Failed to fetch issues. Status code: {issues_response.status_code}")
            break
    return len(issues)


def fetch_most_popular_java_repositories_with_issues(n, issue_number):
    headers = {
        'Authorization': f'Bearer {github_token}'
    }
    params = {
        'q': 'language:java',
        'sort': 'stars',
        'order': 'desc',
    }
    response = requests.get('https://api.github.com/search/repositories', headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        repositories = data['items']
        repositories_with_issues = {}
        for repo in repositories:
            repo_name = repo['name']
            repo_owner = repo['owner']['login']
            issue_len = get_issue_length(repo_owner, repo_name, headers)
            if issue_len > issue_number:
                repository_url = f"https://github.com/{repo_owner}/{repo_name}"
                repositories_with_issues[repository_url] = issue_len
                if len(repositories_with_issues) == n:
                    break
        return repositories_with_issues
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None


if __name__ == '__main__':
    n = 10
    issue_number = 100
    repositories_final = fetch_most_popular_java_repositories_with_issues(n, issue_number)
    json_filename = 'repository_data/repositories.json'
    data_collection_folder = os.path.dirname(json_filename)
    os.makedirs(data_collection_folder, exist_ok=True)
    with open(json_filename, 'w') as json_file:
        json.dump(repositories_final, json_file, indent=4)
    for idx, repo_url in enumerate(repositories_final, start=1):
        print(f"{idx}. {repo_url}")
