import json
import os
import requests

github_token = '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'
headers = {
    'Authorization': f'Bearer {github_token}'
}
def get_pull_request_number(repo_owner: str, repo_name: str) -> int:
    pull_request_url= f"https://api.github.com/search/issues?q=repo:{repo_owner}/{repo_name}+type:issue"
    print(pull_request_url)
    response = requests.get(pull_request_url, headers=headers)
    if response.status_code == 200:
        if "total_count" in response.json():
            number_of_pull_requests = response.json()["total_count"]
            print(number_of_pull_requests)
    else:
        print(response.status_code)
        return 0
    return number_of_pull_requests


#Java programming language
#Popularity (Based on stars)
#Works with GitHub issues (Minimum 500 open or closed issues)
#Active repositories (Had their code updated since 2022-01-01)
#Have been around (Were created before 2021-01-01)
#Considerable size (Size over 2MB)

def min_size_in_bytes():
    size = 2 * 1024 * 1024
    return size


def fetch_most_popular_java_repositories_with_issues(number_of_repositories, issue_number):
    params = {
        # Java programming language
        # Size greater 2MB
        'q': f'language:java size:>{min_size_in_bytes()}',
        'sort': 'stars',
        'order': 'desc',
        'page' : '1',
        'per_page': '200',
        # Updated after the given time
        'since': '2022-01-01T00:00:00Z',
        # Updated before the given time
        'before' : '2021-01-01T00:00:00Z',
    }

    response = requests.get('https://api.github.com/search/repositories', headers=headers, params=params)

    repositories_too_little_issues = 0
    if response.status_code == 200:
        data = response.json()
        repositories = data['items']
        repositories_with_issues = {}
        for repo in repositories:
            repo_name = repo['name']
            repo_owner = repo['owner']['login']
            issue_len = get_pull_request_number(repo_owner, repo_name)
            if issue_len > issue_number:
                repository_url = f"https://github.com/{repo_owner}/{repo_name}"
                repositories_with_issues[repository_url] = issue_len
                print("Repository taken " + repository_url)
                if len(repositories_with_issues) == number_of_repositories:
                    break
            else:
                repositories_too_little_issues+=1
        print("Repositories with issues: " + str(repositories_with_issues))
        print("Repositories with too little issues: " + str(repositories_too_little_issues))
        return repositories_with_issues
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

if __name__ == '__main__':
    number_of_repositories = 40
    issue_number = 500
    repositories_final = fetch_most_popular_java_repositories_with_issues(number_of_repositories, issue_number)
    json_filename = 'repository_data/repositories.json'
    data_collection_folder = os.path.dirname(json_filename)
    os.makedirs(data_collection_folder, exist_ok=True)
    with open(json_filename, 'w') as json_file:
        json.dump(repositories_final, json_file, indent=4)
    for idx, repo_url in enumerate(repositories_final, start=1):
        print(f"{idx}. {repo_url}")
