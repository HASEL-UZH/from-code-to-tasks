import os
import shutil

def all_modifications_include_comments(file_path):
    # Check if all modifications in a file include comments
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('+') or line.startswith('-'):
                if not line[1:].strip().startswith(('*', '//')):
                    return False
    return True

def traverse_and_copy_folders(source_folder, destination_folder):
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    for folder_name in os.listdir(source_folder):
        folder_path = os.path.join(source_folder, folder_name)
        if os.path.isdir(folder_path):
            # Check if all modifications in diff files include comments
            diff_files = [file for file in os.listdir(folder_path) if file.endswith(".diff")]

            if all(not all_modifications_include_comments(os.path.join(folder_path, diff_file)) for diff_file in diff_files):
                destination_path = os.path.join(destination_folder, folder_name)
                shutil.copytree(folder_path, destination_path)

if __name__ == '__main__':
    source_folder_path = "../commit_data_removed_empty"
    destination_folder_path = "../commit_data_removed_empty_and_only_comments"
    traverse_and_copy_folders(source_folder_path, destination_folder_path)
