import json
import os


def duplicate_pr_checker():
    folder_path = "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"

    folder_path = os.path.join(os.path.dirname(__file__), folder_path)

    pr_folders = {}

    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            # Iterate through folders (excluding files)
            for dir_name in dirs:
                commit_info_file_path = os.path.join(root, dir_name, 'commit_info.json')
                if os.path.exists(commit_info_file_path):
                    with open(commit_info_file_path, 'r') as commit_info_file:
                        commit_info_data = json.load(commit_info_file)
                        pull_request = commit_info_data.get("pull request")
                        if pull_request:
                            folder_name = dir_name
                            if pull_request in pr_folders:
                                pr_folders[pull_request].append(folder_name)
                            else:
                                pr_folders[pull_request] = [folder_name]

        # Remove key-value pairs where the value is an array of length 1
        for k, v in list(pr_folders.items()):
            if len(v) == 1:
                del pr_folders[k]
    print(len(pr_folders))
    return pr_folders




if __name__ == "__main__":
    print(duplicate_pr_checker())