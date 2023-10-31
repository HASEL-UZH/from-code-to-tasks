import os
import re


def java_file_counter():
    folder_path = "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"

    folder_path = os.path.join(os.path.dirname(__file__), folder_path)

    number_of_java_files = 0
    if os.path.exists(folder_path) and os.path.isdir(folder_path):

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if re.search(r"ast\.json$", file) and not re.search(r"meta_ast\.json$", file):
                    number_of_java_files +=1

    return number_of_java_files


if __name__ == "__main__":
    print(java_file_counter())