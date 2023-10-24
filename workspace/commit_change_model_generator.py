import json
import os

from ast_compare import compare_ast, build_change_tree
from ast_compare_text import generate_change_text_for_file


def ast_meta_file_iterator():
    folder_path = (
        "../0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    )
    for root, dirs, _ in os.walk(folder_path):
        if root != folder_path:
            subfolder_name = os.path.basename(root)
            if subfolder_name == "commit_5_7627ee83d3c431859793a3969622cf272ae6b488":
                print("hello")
            process_subfolder(folder_path, subfolder_name)


def process_subfolder(folder_path, subfolder_name):
    subfolder_path = os.path.join(folder_path, subfolder_name)
    subfolder_files = os.listdir(subfolder_path)
    ast_meta_files = [
        file for file in subfolder_files if file.endswith("_meta_ast.json")
    ]
    pull_request = get_pull_request(
        os.path.join(folder_path, subfolder_name, "commit_info.json")
    )
    json_dict = get_before_after_dict(subfolder_path, ast_meta_files)
    commit_change_object = build_commit_change_object(
        subfolder_path, json_dict, pull_request
    )
    save_commit_change_object(subfolder_path, commit_change_object)


def get_before_after_dict(subfolder_path, ast_meta_files):
    before_after_dict = {}
    processed_files = []
    for ast_meta_file in ast_meta_files:
        file_name = ast_meta_file.replace("_after_meta_ast.json", "").replace(
            "_before_meta_ast.json", ""
        )
        if file_name in processed_files:
            continue
        # Check if the corresponding _before_meta_ast.json or _after_meta_ast.json exists
        before_file = f"{file_name}_before_meta_ast.json"
        after_file = f"{file_name}_after_meta_ast.json"

        before_after_tuple = get_before_after_tuple(
            subfolder_path, before_file, after_file, ast_meta_files
        )

        processed_files.append(file_name)
        before_after_dict[file_name] = before_after_tuple
    return before_after_dict


def get_before_after_tuple(subfolder_path, before_file, after_file, ast_meta_files):
    before_after_tuple = ()
    if before_file in ast_meta_files and after_file in ast_meta_files:
        # Both before and after files exist, load their JSON data into a tuple
        with open(os.path.join(subfolder_path, before_file), "r") as before_file_obj:
            before_json = json.load(before_file_obj)
        with open(os.path.join(subfolder_path, after_file), "r") as after_file_obj:
            after_json = json.load(after_file_obj)
        before_after_tuple = (before_json, after_json)
    else:
        # Only one of before or after files exist, load the available JSON data
        if before_file in ast_meta_files:
            with open(
                os.path.join(subfolder_path, before_file), "r"
            ) as before_file_obj:
                before_after_tuple = (json.load(before_file_obj), None)
        elif after_file in ast_meta_files:
            with open(os.path.join(subfolder_path, after_file), "r") as after_file_obj:
                before_after_tuple = (None, json.load(after_file_obj))
    return before_after_tuple


def build_commit_change_object(subfolder_path, json_dict, pull_request):
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


def get_pull_request(commit_info_file):
    if os.path.exists(commit_info_file):
        with open(commit_info_file, "r") as json_file:
            data = json.load(json_file)
        return data.get("pull request")
    return None


def save_commit_change_object(subfolder_path, commit_change_object):
    os.makedirs(subfolder_path, exist_ok=True)
    output_file = os.path.join(subfolder_path, "commit_change_object.json")
    with open(output_file, "w") as output_file_obj:
        json.dump(commit_change_object, output_file_obj, indent=4)


if __name__ == "__main__":
    ast_meta_file_iterator()
