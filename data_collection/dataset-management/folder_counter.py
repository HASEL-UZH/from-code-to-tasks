import os

# Number of folders
def count_folders_in_folder(folder_path):
    count = 0
    for _, dirs, _ in os.walk(folder_path):
        count += len(dirs)
    return count

# Number of folders per repo
def count_folders_starting_with(folder_path, start_number):
    count = 0
    for _, dirs, _ in os.walk(folder_path):
        for dir_name in dirs:
            folder_start = dir_name[7]
            if folder_start== str(start_number):
                count += 1
    return count

# Number of folders with multiple .diff files
def folders_with_multiple_diff_files(commit_data_folder):
    folders_with_multiple_diffs = []

    if os.path.exists(commit_data_folder) and os.path.isdir(commit_data_folder):
        for folder_name in os.listdir(commit_data_folder):
            folder_path = os.path.join(commit_data_folder, folder_name)
            if os.path.isdir(folder_path):
                diff_file_count = sum(1 for file in os.listdir(folder_path) if file.endswith('.diff'))
                if diff_file_count > 1:
                    folders_with_multiple_diffs.append(folder_name)

    return folders_with_multiple_diffs


if __name__ == "__main__":
    folder_path = "../commit_data_removed_empty"

    folder_count_total = count_folders_in_folder(folder_path)
    print(f"Total number of folders in '{folder_path}': {folder_count_total}")

    start_numbers = [0,1,2,3,4,5,6,7,8,9]
    for start_number in start_numbers:
        folder_count_per_repository = count_folders_starting_with(folder_path, start_number)
        print(f"Total number of folders in commit_data of repository {start_number} '{folder_path} of repository {start_number}': {folder_count_per_repository}")

    folders_with_multiple_diffs = folders_with_multiple_diff_files(folder_path)

    # Print the folder names
    print("Folders with multiple .diff files:")
    for folder_name in folders_with_multiple_diffs:
        print(folder_name)
    print("LEN: " + str(len(folders_with_multiple_diffs)) )