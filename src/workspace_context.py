import json
import os
import re

GITHUB_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}


WORKSPACE_ROOT = os.path.abspath("./_workspace")

DATASETS_DIR = os.path.join(WORKSPACE_ROOT, "datasets")
COMMIT_DATA_DIR = os.path.join(DATASETS_DIR, "commit_data")
REPOSITORIES_DIR = os.path.join(WORKSPACE_ROOT, "repositories")

CANDIDATE_REPOSITORY_FILE = "candidate_repositories.json"
FINAL_REPOSITORY_FILE = "final_repositories.json"

# Get dir
def get_repository_dir():
    return get_or_create_dir(REPOSITORIES_DIR)

def get_datasets_dir():
    return get_or_create_dir(DATASETS_DIR)

def get_commit_data_dir():
    return get_or_create_dir(COMMIT_DATA_DIR)

# Get file path

def get_repository_file_path(file_name):
    return os.path.join(get_repository_dir(), file_name)

def get_datasets_file_path(file_name):
    return os.path.join(get_datasets_dir(), file_name)

# Create dir if it doesn't already exist

def get_or_create_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# Get repository data

def get_commit_repository_dir_path(repo_id):
    dir_name = get_or_create_dir(os.path.join(get_commit_data_dir(), str(repo_id)))
    return dir_name
def get_commit_data_dir_path(repo_id, commit_hash):
    dir_name = os.path.join(get_commit_repository_dir_path(repo_id), f"commit_{repo_id}_{commit_hash}")
    return get_or_create_dir(dir_name)

def get_commit_data_file_before(repo_id, commit_hash, file_name):
    return os.path.join(get_commit_data_dir_path(repo_id, commit_hash), f"{get_file_name_without_extension(file_name)}_before.java")

def get_commit_data_file_after(repo_id, commit_hash, file_name):
    return os.path.join(get_commit_data_dir_path(repo_id, commit_hash), f"{get_file_name_without_extension(file_name)}_after.java")

def get_commit_data_file_diff(repo_id, commit_hash, file_name):
    return os.path.join(get_commit_data_dir_path(repo_id, commit_hash), f"{get_file_name_without_extension(file_name)}.diff")

def get_commit_data_file_info(repo_id, commit_hash):
    return os.path.join(get_commit_data_dir_path(repo_id, commit_hash), f"commit_info.json")

# Get file names
def get_file_name_without_extension(file_name):
    return os.path.splitext(file_name)[0]

def get_file_name_without_ast_extension(file_name):
    return file_name.split("_", 1)[0]

def get_ast_for_java_source_file(file_name):
    ast_file_name = (re.sub(r"(\.java)", "", os.path.splitext(file_name)[0]) + "_ast.json")
    return ast_file_name

def get_meta_ast_for_ast_source_file(file_name):
    meta_ast_file_name = file_name.replace("ast.json", "meta_ast.json")
    return meta_ast_file_name

# Check file type

def is_java_file(file_name):
    return file_name.endswith(".java")

def is_ast_file(file_name):
    return file_name.endswith("ast.json") and not file_name.endswith("meta_ast.json")

def is_ast_meta_file(file_name):
    return file_name.endswith("meta_ast.json")


# Load json
def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data

# Write json
def write_json_file(file_path, file_content):
    with open(file_path, "w") as json_file:
        json.dump(file_content, json_file, indent=4)

def write_text_file(file_path, file_content, opts={}):
    if opts and opts["no_empty_file"] and file_content is None:
        return
    with open(file_path, "w") as file:
        file.write(file_content)

def get_pull_request(file_path):
    commit_info_file_path = os.path.join(file_path, "commit_info.json")
    data = load_json_file(commit_info_file_path)
    return data["pull request"]