import os


def delete_empty_files():
    folder_path = (
        "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    )
    folder_path = os.path.join(os.path.dirname(__file__), folder_path)

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Check if the file is empty
                if os.path.getsize(file_path) == 0:
                    # Delete the empty file
                    print("deleted " + file_path)
                    os.remove(file_path)


if __name__ == "__main__":
    delete_empty_files()
