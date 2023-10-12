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

def copy_folder_structure(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        destination_item = os.path.join(destination_folder, item)

        if os.path.isdir(source_item):
            copy_folder_structure(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)

def create_dataset_n(n):
    # Path to the original folder
    original_folder = "../commit_data"

    # Path to the new folder
    new_folder = concatenated_string = f"../commit_data_{n}"

    # Create the new folder if it doesn't exist
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    # Get a list of subfolders in the original folder
    subfolders = [f for f in os.listdir(original_folder) if os.path.isdir(os.path.join(original_folder, f))]

    # Choose n random subfolders
    selected_subfolders = random.sample(subfolders, min(n, len(subfolders)))

    # Copy the selected subfolders and their structure to the new folder
    for subfolder in selected_subfolders:
        source_path = os.path.join(original_folder, subfolder)
        destination_path = os.path.join(new_folder, subfolder)
        copy_folder_structure(source_path, destination_path)


if __name__ == "__main__":
    n = 500
    commit_data_folder = "../commit-data"
    #create_dataset_removed_empty()
    create_dataset_n(n)