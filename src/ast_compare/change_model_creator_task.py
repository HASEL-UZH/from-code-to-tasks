import os

from ast_compare import compare_ast, build_change_tree
from ast_compare_text import generate_change_text_for_file
from src.repository_manager import get_repositories, get_repository_commits, get_repository_commit_files
from src.workspace_context import write_json_file, is_ast_meta_file, \
    get_file_name_without_ast_extension, load_json_file, get_commit_data_dir_path, get_pull_request


def get_before_after_dict(ast_meta_files):
    before_after_dict = {}
    processed_files = []
    for ast_meta_file in ast_meta_files:
        file_name = get_file_name_without_ast_extension(ast_meta_file["file_name"])
        if file_name in processed_files:
            continue
        before_file_name = f"{file_name}_before_meta_ast.json"
        after_file_name = f"{file_name}_after_meta_ast.json"
        before_after_json_tuple = get_before_after_json_tuple(before_file_name, after_file_name, ast_meta_files)
        processed_files.append(file_name)
        before_after_dict[file_name] = before_after_json_tuple
    return before_after_dict


def get_before_after_json_tuple(before_file_name, after_file_name, ast_meta_files):
    before_file = None
    after_file = None
    for ast_meta_file in ast_meta_files:
        if ast_meta_file["file_name"] == before_file_name:
            before_file = load_json_file(ast_meta_file["file_path"])
        if ast_meta_file["file_name"] == after_file_name:
            after_file = load_json_file(ast_meta_file["file_path"])
    before_and_after_tuple = (before_file, after_file)
    return before_and_after_tuple



def build_commit_change_object(json_dict, pull_request):
    commit_compare_text = ""
    commit_change_object = {
        "pr": {"text": pull_request},
        "code": {"text": "", "details": []},
    }
    for file_name, change_tuple in json_dict.items():
        before_meta_ast, after_met_ast = change_tuple
        ast_compare_flat = compare_ast(before_meta_ast, after_met_ast)
        try:
            ast_compare_tree = build_change_tree(ast_compare_flat)
        except:
            ast_compare_tree = {}
            pass
        commit_change_object["code"]["details"].append(ast_compare_tree)
        ast_file_change_text = generate_change_text_for_file(
            file_name, ast_compare_tree
        )
        commit_compare_text += ast_file_change_text
        commit_change_object["code"]["text"] = commit_compare_text
    return commit_change_object


def change_model_creator_task():
    repositories = get_repositories()
    for repository in repositories:
        commits = get_repository_commits(repository["id"])
        for commit in commits:
            commit_files = get_repository_commit_files(commit["repo_id"], commit["commit_hash"])
            ast_meta_files = [commit_file for commit_file in commit_files if is_ast_meta_file(commit_file["file_name"])]
            commit_change_dictionary = get_before_after_dict(ast_meta_files)
            pull_request = get_pull_request(get_commit_data_dir_path(commit["repo_id"], commit["commit_hash"]))
            commit_change_object = build_commit_change_object(commit_change_dictionary, pull_request)
            write_json_file(os.path.join(get_commit_data_dir_path(commit["repo_id"], commit["commit_hash"]), "commit_change_object.json"), commit_change_object)
            print(f"wrote commit change object for commit {commit['commit_hash']} in repo {commit['repo_id']}")

if __name__ == "__main__":
    change_model_creator_task()
