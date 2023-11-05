import time

import requests

from src.object_factory import ObjectFactory
from src.object_store import db
from src.workspace_context import HEADERS
from src.utils.profiler import Profiler


def create_repository_task(url_excludes=[]):
    print("create_repository_task started")
    profiler = Profiler()

    url_excludes = url_excludes or ["https://github.com/Snailclimb/JavaGuide","https://github.com/facebook/react-native"]
    number_of_repositories = 100 # Maximum is 100
    issue_minimum = 500
    pr_minimum = 500
    repository_urls = fetch_most_popular_java_repositories_with_issues(
        number_of_repositories, issue_minimum, pr_minimum
    )
    filtered_urls = [value for value in repository_urls if value not in url_excludes]
    for url in filtered_urls:
        repository = ObjectFactory.repository(url)
        db.save_repository(repository)

    profiler.checkpoint(f"create_commit_data_task done: total repositories: {len(filtered_urls)}")
    db.invalidate()


def get_issue_pr_number(repo_owner: str, repo_name: str, type: str) -> int:
    try:
        issue_pr_url = f"https://api.github.com/search/issues?q=repo:{repo_owner}/{repo_name}+is:{type}"
        response = requests.get(issue_pr_url, headers=HEADERS)
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


def fetch_most_popular_java_repositories_with_issues(
    number_of_repositories, issue_minimum, pr_minimum
):
    print("FIXME - fetch_most_popular_java_repositories_with_issues: remove static data")
    return [
         "https://github.com/iluwatar/java-design-patterns",
     ]

    params = {
        "q": f"language:java",
        "sort": "stars",
        "order": "desc",
        "page": "1",
        "per_page": str(number_of_repositories),
        "since": "2022-01-01T00:00:00Z",
        "before": "2021-01-01T00:00:00Z",
    }
    response = requests.get(
        "https://api.github.com/search/repositories", headers=HEADERS, params=params
    )
    if response.status_code == 200:
        data = response.json()
        repositories = data["items"]
        candidate_repositories = []
        for repo in repositories:
            repo_name = repo["name"]
            print(repo_name)
            repo_owner = repo["owner"]["login"]
            issue_number = get_issue_pr_number(repo_owner, repo_name, "issue")
            pr_number = get_issue_pr_number(repo_owner, repo_name, "pr")

            if issue_number > issue_minimum and pr_number > pr_minimum:
                repository_url = f"https://github.com/{repo_owner}/{repo_name}"
                candidate_repositories.append(repository_url)
            else:
                continue
        return candidate_repositories
    else:
        return None


if __name__ == "__main__":
    # print("TASK DISABLED"); exit(0)
    create_repository_task()