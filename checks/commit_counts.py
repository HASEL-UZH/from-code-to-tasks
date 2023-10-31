import os

directory_path = (
    "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
)

if os.path.exists(directory_path) and os.path.isdir(directory_path):
    folder_count = sum(1 for entry in os.scandir(directory_path) if entry.is_dir())
    print(f"Number of folders in '{directory_path}': {folder_count}")
else:
    print(f"The directory '{directory_path}' does not exist or is not a directory.")
