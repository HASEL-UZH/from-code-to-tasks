import os

from src.workspace_context import load_json_file, FINAL_REPOSITORY_FILE, get_commit_repository_dir_path, \
    get_commit_data_dir_path, get_repository_file_path


def get_repositories():
    repository_file_path = get_repository_file_path(FINAL_REPOSITORY_FILE)
    repository_json = load_json_file(repository_file_path)
    return repository_json["final_repositories"]

def get_repository_commits(repo_id):
    repository_dir = get_commit_repository_dir_path(repo_id)
    commits = []
    for root, dirs, files in os.walk(repository_dir):
        for dir in dirs:
            commit_hash = dir.rsplit("_", 1)[-1]
            commit = {
                "repo_id" : repo_id,
                "commit_hash" : commit_hash
            }
            commits.append(commit)
    return commits

def get_repository_commit_files(repo_id, commit_hash):
    commit_dir = get_commit_data_dir_path(repo_id, commit_hash)
    file_infos = []
    for root, dirs, files in os.walk(commit_dir):
        for file in files:
            file_info = {
                "repo_id" : repo_id,
                "commit_hash" : commit_hash,
                "dir_name" : commit_dir,
                "file_name" : file,
                "file_path" : os.path.join(commit_dir, file)
            }
            file_infos.append(file_info)
    return file_infos


