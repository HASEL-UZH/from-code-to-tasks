import os
import re
import subprocess


def java_file_iterator():
    folder_path = (
        "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    )
    folder_path = os.path.join(os.path.dirname(__file__), folder_path)
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".java"):
                    in_file_path = os.path.join(root, file)
                    out_file_name = (
                        re.sub(r"(\.java)", "", os.path.splitext(file)[0]) + "_ast.json"
                    )
                    out_file_path = os.path.join(root, out_file_name)
                    ast_creator(in_file_path, out_file_path)
                    print("ast created for file " + file)


def ast_creator(in_file, out_file):
    command = [
        "java",
        "-jar",
        "./ast_workspace/ast-meta-werks-0.1.1.jar",
        in_file,
        out_file,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(in_file + " did not work. ")
        return
    return result.stdout.strip()


if __name__ == "__main__":
    java_file_iterator()
