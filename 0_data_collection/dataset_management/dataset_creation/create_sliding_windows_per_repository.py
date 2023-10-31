import json
import os
import shutil
from datetime import date


def copy_specific_files(src_path, dst_path):
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file in ["commit_info.json", "commit_change_object.json"]:
                src_file_path = os.path.join(root, file)
                dst_file_path = os.path.join(
                    dst_path, os.path.relpath(src_file_path, src_path)
                )
                os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
                shutil.copy(src_file_path, dst_file_path)


def get_pull_request(commit_info_path):
    pull_request = None
    if os.path.isfile(commit_info_path):
        with open(commit_info_path, "r") as commit_info_file:
            commit_info = json.load(commit_info_file)
            if commit_info and "pull request" in commit_info:
                pull_request = commit_info["pull request"]
    return pull_request


def create_sliding_window_folders(input_folder, output_folder, desired_window_size):
    commit_dates = read_commit_dates(input_folder)
    unique_pull_requests = set()
    commit_per_window = 0
    window_counter = 1
    for i in range(len(commit_dates)):
        commit_names_in_window = []
        if i == 3036:
            pass
        if window_counter == 718:
            pass
        first_commit_in_window = commit_dates[i]
        src_path = os.path.join(input_folder, first_commit_in_window)
        pull_request = get_pull_request(os.path.join(src_path, "commit_info.json"))
        if pull_request:
            unique_pull_requests.add(pull_request)
            commit_per_window += 1
            commit_names_in_window.append(first_commit_in_window)
        for j in range(i + 1, len(commit_dates)):
            if len(unique_pull_requests) != desired_window_size:
                following_commit_in_window = commit_dates[j]
                src_path = os.path.join(input_folder, following_commit_in_window)
                pull_request = get_pull_request(
                    os.path.join(src_path, "commit_info.json")
                )
                if pull_request:
                    unique_pull_requests.add(pull_request)
                    commit_per_window += 1
                    commit_names_in_window.append(following_commit_in_window)

            if len(unique_pull_requests) == desired_window_size:
                sliding_window_folder = os.path.join(
                    output_folder, f"sliding_window_{window_counter}"
                )
                os.makedirs(sliding_window_folder, exist_ok=True)
                for commit_name in commit_names_in_window:
                    dst_path = os.path.join(sliding_window_folder, commit_name)
                    src_path = os.path.join(input_folder, commit_name)
                    copy_specific_files(src_path, dst_path)
                unique_pull_requests.clear()
                window_counter += 1
                commit_per_window = 0
                break


def read_commit_dates(folder_path):
    commit_dates = []
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        commit_info_path = os.path.join(subfolder_path, "commit_info.json")

        if os.path.isfile(commit_info_path):
            with open(commit_info_path, "r") as commit_info_file:
                commit_info = json.load(commit_info_file)
                committer_date = commit_info.get("committer date")
                if committer_date:
                    commit_dates.append(
                        (
                            date(
                                committer_date[2], committer_date[1], committer_date[0]
                            ),
                            subfolder,
                        )
                    )
    commit_dates.sort(key=lambda x: x[0])
    return [subfolder for _, subfolder in commit_dates]


if __name__ == "__main__":
    desired_window_size = 30  # Adjust this value to your desired window size
    commit_data_per_repository_folder = "../../datasets/commit_data_per_repository"
    for folder in os.listdir(commit_data_per_repository_folder):
        print(folder)
        input_folder = os.path.join(commit_data_per_repository_folder, folder)
        output_folder = os.path.join(
            f"../../datasets/commit_data_sliding_window_per_repository_{desired_window_size}",
            folder,
        )
        os.makedirs(output_folder, exist_ok=True)
        create_sliding_window_folders(input_folder, output_folder, desired_window_size)
