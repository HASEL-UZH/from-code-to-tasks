import requests

github_token = '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'
headers = {
    'Authorization': f'Bearer {github_token}'
}
def get_pull_request_number(repo_owner: str, repo_name: str) -> int:
    pull_request_url= f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=all"
    print(pull_request_url)
    response = requests.get(pull_request_url, headers=headers)
    if response.status_code == 200:
        number_of_pull_requests = len(response.json())
    else:
        print('Status code: '+str(response.status_code))
        return 0
    return number_of_pull_requests


if __name__ == '__main__':
   number_of_pull_requests = get_pull_request_number('realm', 'realm-java')
   print(number_of_pull_requests)
