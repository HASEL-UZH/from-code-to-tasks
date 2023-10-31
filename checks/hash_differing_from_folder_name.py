import json
import os

path = "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
mismatched_folders = []

for folder_name in os.listdir(path):
    folder_path = os.path.join(path, folder_name)

    # Extract the number after the last underscore from the folder name
    folder_number = folder_name.rsplit("_", 1)[-1]

    # Check if the commit_info.json file exists in the folder
    commit_info_file = os.path.join(folder_path, "commit_info.json")

    if os.path.isfile(commit_info_file):
        with open(commit_info_file, "r") as json_file:
            commit_info = json.load(json_file)

            # Extract the commit hash from the JSON file
            commit_hash = commit_info.get("commit hash", "")

            # Compare the extracted number with the commit hash
            if folder_number != commit_hash:
                mismatched_folders.append(folder_name)

# Return the array of mismatched folder names
print(mismatched_folders)
