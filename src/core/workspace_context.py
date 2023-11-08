import json
import os

GITHUB_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}



STORE_ROOT = os.path.abspath("./_store")
RESULTS_DIR = os.path.abspath("./results")


def get_store_dir(path=None):
    full_path = STORE_ROOT
    if path:
        full_path = os.path.join(STORE_ROOT, path)
    return get_or_create_dir(full_path)

def get_results_dir():
    return get_or_create_dir(RESULTS_DIR)


# --- Check file type

def is_java_file(file_name):
    return file_name.endswith(".java")


def is_ast_file(file_name):
    return file_name.endswith("ast.json") and not file_name.endswith("meta_ast.json")


def is_ast_meta_file(file_name):
    return file_name.endswith("meta_ast.json")

# returns the file extensions including the '.'
def get_file_ext(file_name):
    _, ext = os.path.splitext(file_name)
    return ext


# returns the file extensions without the '.'
def get_file_ext_name(file_name):
    _, ext = os.path.splitext(file_name)
    return ext[1:]

def get_file_base_name(file_name):
    base, _ = os.path.splitext(file_name)
    return base

# --- File IO

def get_or_create_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# Load json
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data

def read_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        return content

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
    data = read_json_file(commit_info_file_path)
    return data["pull request"]

