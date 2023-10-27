import json
import os
import shutil
from datetime import date

# Constants
WINDOW_SIZE = 20


def copy_specific_files(src_path, dst_path):
    # Function to copy specific files from src_path to dst_path
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file in ["commit_info.json", "commit_change_object.json"]:
                src_file_path = os.path.join(root, file)
                dst_file_path = os.path.join(
                    dst_path, os.path.relpath(src_file_path, src_path)
                )
                os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
                shutil.copy(src_file_path, dst_file_path)


def read_commit_dates(folder_path):
    # Function to read commit dates from the given folder
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


def create_sliding_window_folders(input_folder, output_folder):
    # Function to create sliding window folders based on commit dates
    commit_dates = read_commit_dates(input_folder)
    for i in range(len(commit_dates) - WINDOW_SIZE + 1):
        window_subfolders = commit_dates[i : i + WINDOW_SIZE]
        sliding_window_folder = os.path.join(f"{output_folder}/sliding_window_{i + 1}")
        os.makedirs(sliding_window_folder)
        for subfolder in window_subfolders:
            src_path = os.path.join(input_folder, subfolder)
            dst_path = os.path.join(sliding_window_folder, subfolder)
            copy_specific_files(src_path, dst_path)


if __name__ == "__main__":
    commit_data_per_repository_folder = "../../datasets/commit_data_per_repository"

    # Iterate through subdirectories in commit_data_per_repository_folder
    for folder in os.listdir(commit_data_per_repository_folder):
        print(folder)
        input_folder = os.path.join(commit_data_per_repository_folder, folder)

        # Check if the item is a directory
        if os.path.isdir(input_folder):
            output_folder = os.path.join(
                "../../datasets/commit_data_sliding_window_per_repository", folder
            )
            os.makedirs(output_folder, exist_ok=True)
            create_sliding_window_folders(input_folder, output_folder)
