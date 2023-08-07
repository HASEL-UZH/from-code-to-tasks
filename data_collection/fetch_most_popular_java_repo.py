import requests
import json
import os

# GitHub API token for authentication (Replace 'YOUR_GITHUB_TOKEN' with your actual token)
GITHUB_TOKEN = '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'


# Function to fetch the most popular Java repository
def fetch_most_popular_java_repo():
    url = 'https://api.github.com/search/repositories'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    params = {'q': 'language:java', 'sort': 'stars', 'order': 'desc', 'per_page': 1}

    try:
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            repo_data = response.json()
            if 'items' in repo_data and len(repo_data['items']) > 0:
                most_popular_repo = repo_data['items'][0]
                return most_popular_repo
            else:
                print("No Java repositories found.")
                return None
        else:
            print(f"Failed to fetch repositories. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching repositories: {e}")
        return None


# Function to fetch the last 5 commits of a repository and save the data
def fetch_last_5_commits(repo_owner, repo_name):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    params = {'per_page': 5}

    try:
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            commits = response.json()

            # Save the commits data to a file in the 'data' folder
            data_folder = 'data'
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)

            data_file = os.path.join(data_folder, f"{repo_owner}_{repo_name}_commits.json")
            with open(data_file, 'w') as file:
                json.dump(commits, file, indent=2)

            return commits
        else:
            print(f"Failed to fetch commits from {repo_owner}/{repo_name}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching commits: {e}")
        return None


# Main function to collect data from the most popular Java repository
def main():
    most_popular_repo = fetch_most_popular_java_repo()

    if most_popular_repo:
        repo_owner = most_popular_repo['owner']['login']
        repo_name = most_popular_repo['name']

        print(f"Most popular Java repository: {repo_owner}/{repo_name}")

        commits = fetch_last_5_commits(repo_owner, repo_name)
        if commits:
            print("Last 5 commits:")
            for commit in commits:
                print(commit['commit']['message'])
        else:
            print("No commits found for the repository.")
    else:
        print("No Java repositories found. Cannot proceed with data collection.")


if __name__ == '__main__':
    main()
