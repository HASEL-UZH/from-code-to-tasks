import os
import shutil

def find_missing_commit_info_files(commit_data_folder):
    # Find folders missing commit_info.json files.
    missing_commit_info_files = []
    for folder_name in os.listdir(commit_data_folder):
        folder_path = os.path.join(commit_data_folder, folder_name)
        if os.path.isdir(folder_path):
            commit_info_path = os.path.join(folder_path, 'commit_info.json')
            if not os.path.exists(commit_info_path):
                missing_commit_info_files.append(folder_name)
    return missing_commit_info_files

def find_folders_without_diff_files(commit_data_folder):
    # Find folders without .diff files.
    folders_without_diff_files = []
    if os.path.exists(commit_data_folder) and os.path.isdir(commit_data_folder):
        for folder_name in os.listdir(commit_data_folder):
            folder_path = os.path.join(commit_data_folder, folder_name)
            if os.path.isdir(folder_path):
                # Check if no file ends with ".diff"
                diff_files = [file for file in os.listdir(folder_path) if file.endswith(".diff")]
                if not diff_files:
                    folders_without_diff_files.append(folder_name)
    return folders_without_diff_files

def move_files_not_missing(commit_data_folder):
    # Move folders with commit_info.json files to a different location.
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

if __name__ == '__main__':
    commit_data_folder = "../commit_data"

    # Find missing commit_info.json files
    missing_commit_info_files = find_missing_commit_info_files(commit_data_folder)
    missing_diff_files = find_folders_without_diff_files(commit_data_folder)

    print("Folders missing commit_info.json files:")
    for folder_name in missing_commit_info_files:
        print(folder_name)
    print("Number of missing commit_info.json files: " + str(len(missing_commit_info_files)))

    print("Folders missing .diff files:")
    for folder_name in missing_diff_files:
        print(folder_name)
    print("Number of missing .diff files: " + str(len(missing_diff_files)))

    # Check if the same repositories are missing both commit_info.json and .diff files
    print("Same repos: " + str(set(missing_commit_info_files) == set(missing_diff_files)))

    # 319 repos have missing commit_info and diff files!
