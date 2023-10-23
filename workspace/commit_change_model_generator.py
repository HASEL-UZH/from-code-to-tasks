import json
import os
import re

from ast_compare import compare_ast, build_change_tree
from ast_compare_text import generate_change_text_for_file


def ast_meta_file_iterator():
    folder_path = (
        "../0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    )
    for root, dirs, files in os.walk(folder_path):
        if root != folder_path:
            subfolder_name = os.path.basename(root)
            subfolder_files = [file for file in files]
            ast_meta_files = [
                file for file in subfolder_files if file.endswith("_meta_ast.json")
            ]
            commit_info_file = os.path.join(root, "commit_info.json")

            if os.path.exists(commit_info_file):
                with open(commit_info_file, "r") as json_file:
                    data = json.load(json_file)

                pull_request = data.get("pull request")

            json_dict = {}
            processed_files = []

            for ast_meta_file in ast_meta_files:
                file_name = re.match(r"[^_]+", ast_meta_file).group(0)
                if file_name in processed_files:
                    continue
                # Check if the corresponding _before_meta_ast.json or _after_meta_ast.json exists
                before_file = f"{file_name}_before_meta_ast.json"
                after_file = f"{file_name}_after_meta_ast.json"

                json_tuple = ()
                if before_file in ast_meta_files and after_file in ast_meta_files:
                    # Both before and after files exist, load their JSON data into a tuple
                    with open(
                        os.path.join(folder_path, subfolder_name, before_file), "r"
                    ) as before_file_obj:
                        before_json = json.load(before_file_obj)
                    with open(
                        os.path.join(folder_path, subfolder_name, after_file), "r"
                    ) as after_file_obj:
                        after_json = json.load(after_file_obj)
                    json_tuple = (before_json, after_json)
                else:
                    # Only one of before or after files exist, load the available JSON data
                    if before_file in ast_meta_files:
                        with open(
                            os.path.join(folder_path, subfolder_name, before_file), "r"
                        ) as before_file_obj:
                            json_tuple = (json.load(before_file_obj), None)
                    elif after_file in ast_meta_files:
                        with open(
                            os.path.join(folder_path, subfolder_name, after_file), "r"
                        ) as after_file_obj:
                            json_tuple = (None, json.load(after_file_obj))
                processed_files.append(file_name)
                # Dictionary with file_names as keys and tuple (before json, after json) before json or after json can be None
                json_dict[file_name] = json_tuple
            commit_compare_text = ""
            commit_change_object = {
                "pr": {"text": pull_request},
                "code": {"text": "", "details": []},
            }
            for file_name, change_tuple in json_dict.items():
                before_meta_ast, after_met_ast = change_tuple
                ast_compare_flat = compare_ast(before_meta_ast, after_met_ast)
                ast_compare_tree = build_change_tree(ast_compare_flat)
                commit_change_object["code"]["details"].append(ast_compare_tree)
                ast_file_change_text = generate_change_text_for_file(
                    file_name, ast_compare_tree
                )
                commit_compare_text += ast_file_change_text
            commit_change_object["code"]["text"] = commit_compare_text
            pass

            # Define the subfolder path to save the file
            subfolder_path = os.path.join(folder_path, subfolder_name)

            # Create the output folder if it doesn't exist
            os.makedirs(subfolder_path, exist_ok=True)

            # Define the output file path
            output_file = os.path.join(subfolder_path, "commit_change_object.json")

            # Write the commit_change_object to the output file
            with open(output_file, "w") as output_file_obj:
                json.dump(commit_change_object, output_file_obj, indent=4)


if __name__ == "__main__":
    ast_meta_file_iterator()
