import os
import shutil
import random

def create_dataset_removed_empty(commit_data_folder):
    missing_commit_info_files = []
    if os.path.exists(commit_data_folder) and os.path.isdir(commit_data_folder):
        for folder_name in os.listdir(commit_data_folder):
            folder_path = os.path.join(commit_data_folder, folder_name)
            if os.path.isdir(folder_path):
                commit_info_path = os.path.join(folder_path, 'commit_info.json')
                if not os.path.exists(commit_info_path):
                    missing_commit_info_files.append(folder_name)
                else:
                    print('in else')
                    # Copy the folder to commit_data_removed_empty
                    dest_path = os.path.join('../commit_data_removed_empty', folder_name)
                    shutil.copytree(folder_path, dest_path)
    return missing_commit_info_files

if __name__ == "__main__":
    commit_data_folder = "../commit_data"
    create_dataset_removed_empty()
