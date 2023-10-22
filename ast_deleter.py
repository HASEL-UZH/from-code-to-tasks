import os

def ast_deleter():
    folder_path = "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"

    folder_path = os.path.join(os.path.dirname(__file__), folder_path)

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith("meta_ast.json"):
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    print(file + " removed")


if __name__ == "__main__":
    ast_deleter()

#