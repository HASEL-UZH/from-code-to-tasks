import requests

from src.workspace_context import get_repository_file_path, CANDIDATE_REPOSITORY_FILE, load_json_file, write_json_file, \
    FINAL_REPOSITORY_FILE


def get_stargazers_mapping(candidate_repository_urls):
    stargazers_mapping = {}
    for repository_url in candidate_repository_urls:
        request_url = f"https://api.github.com/repos/{repository_url[19:]}"
        response = requests.get(request_url)
        if response.status_code == 200:
            repo_info = response.json()
            stargazers_count = repo_info["stargazers_count"]
            stargazers_mapping[repository_url] = stargazers_count
    return stargazers_mapping


def get_ten_most_popular(stargazers_mapping):
    sorted_repos = sorted(stargazers_mapping.items(), key=lambda x: x[1], reverse=True)
    top_10_repos = sorted_repos[:10]
    top_10_repo_urls = [repo[0] for repo in top_10_repos]
    return top_10_repo_urls

def rank_candidate_repository_task():
    repository_file_path = get_repository_file_path(CANDIDATE_REPOSITORY_FILE)
    repository_json = load_json_file(repository_file_path)
    candidate_repository_urls = repository_json["candidate_repositories"]

    stargazers_mapping = get_stargazers_mapping(candidate_repository_urls)
    final_repositories = get_ten_most_popular(stargazers_mapping)
    final_repositories_json = {"final_repositories" : final_repositories}

    repository_file_path = get_repository_file_path(FINAL_REPOSITORY_FILE)
    write_json_file(repository_file_path, final_repositories_json)

if __name__ == "__main__":
    rank_candidate_repository_task()
