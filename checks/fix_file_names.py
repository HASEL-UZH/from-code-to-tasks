import os

def fix_file_names():
    folder_path = "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"

    folder_path = os.path.join(os.path.dirname(__file__), folder_path)

    if os.path.exists(folder_path) and os.path.isdir(folder_path):

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root, file)
                    file_name, file_extension = os.path.splitext(file)
                    # Check if ".java" occurs anywhere except at the end
                    if file.count(".java") > 1:
                        # Remove ".java" from the file name
                        new_file_name = file_name.replace(".java", "")
                        new_file_path = os.path.join(root, new_file_name + file_extension)
                        os.rename(file_path, new_file_path)
                        print(f"Renamed: {file_path} to {new_file_path}")

if __name__ == "__main__":
    fix_file_names()
