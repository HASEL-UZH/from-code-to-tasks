import json
import os

WORKSPACE_ROOT = os.path.abspath("./_workspace")

DATASETS_DIR = os.path.join(WORKSPACE_ROOT, "datasets")
REPOSITORIES_DIR = os.path.join(WORKSPACE_ROOT, "repositories")

CANDIDATE_REPOSITORY_FILE = "candidate_repositories.json"
FINAL_REPOSITORY_FILE = "final_repositories.json"


def get_repository_dir():
    return get_or_create_dir(REPOSITORIES_DIR)

def get_datasets_dir():
    return get_or_create_dir(DATASETS_DIR)

def get_repository_file_path(file_name):
    return os.path.join(get_repository_dir(), file_name)

def get_datasets_file_path(file_name):
    return os.path.join(get_datasets_dir(), file_name)

def get_or_create_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# Load json
def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data

# Write json
def write_json_file(file_path, file_content):
    with open(file_path, "w") as json_file:
        json.dump(file_content, json_file, indent=4)

