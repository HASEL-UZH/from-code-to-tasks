
import os
import json
import shutil
from datetime import date

# Constants
WINDOW_SIZE = 20

def read_commit_dates(folder_path):
    commit_dates = []

    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        commit_info_path = os.path.join(subfolder_path, 'commit_info.json')

        if os.path.isfile(commit_info_path):
            with open(commit_info_path, 'r') as commit_info_file:
                commit_info = json.load(commit_info_file)
                committer_date = commit_info.get('committer date')
                if committer_date:
                    commit_dates.append((date(committer_date[2], committer_date[1], committer_date[0]), subfolder))

    # Sort the folders based on committer date
    commit_dates.sort(key=lambda x: x[0])

    return [subfolder for _, subfolder in commit_dates]

def create_sliding_window_folders(base_folder):
    commit_dates = read_commit_dates(base_folder)
    for i in range(len(commit_dates) - WINDOW_SIZE + 1):
        window_subfolders = commit_dates[i:i + WINDOW_SIZE]

        # Create sliding window subfolder
        sliding_window_folder = os.path.join(base_folder, f'commit_data_sliding_window/sliding_window_{i + 1}')
        os.makedirs(sliding_window_folder)

        # Copy the selected subfolders into the sliding window subfolder
        for subfolder in window_subfolders:
            src_path = os.path.join(base_folder, subfolder)
            dst_path = os.path.join(sliding_window_folder, subfolder)
            shutil.copytree(src_path, dst_path)

if __name__ == "__main__":
    folder_path = "./data_collection/commit_data_removed_empty"
    sliding_window_parent_folder = "./data_collection/commit_data_sliding_window"
    os.makedirs(sliding_window_parent_folder, exist_ok=True)

    create_sliding_window_folders(folder_path)

