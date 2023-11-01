import os

WORKSPACE_ROOT = os.path.abspath("./_workspace")

DATASETS_DIR = os.path.join(WORKSPACE_ROOT, "datasets")
REPOSITORIES_DIR = os.path.join(WORKSPACE_ROOT, "repositories")

CANDIDATE_REPOSITORY_FILE = "candidate_repositories.json"


def get_repository_dir():
    return get_or_create_dir(REPOSITORIES_DIR)


def get_repository_file(file_name):
    return os.path.join(get_repository_dir(), file_name)


def get_or_create_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)
    return dir_name


# Filename caluclations
def getDiffFile(arg):
    pass


def get_xyz_directory():
    pass


def list_files_in_xyz_directory():
    pass
