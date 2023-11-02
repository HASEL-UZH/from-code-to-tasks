import os
import subprocess

from src.repository_manager import get_repositories, get_repository_commits, get_repository_commit_files
from src.workspace_context import is_java_file, get_ast_for_java_source_file


def ast_creator(in_file, out_file):
    command = [
        "java",
        "-jar",
        "./bin/ast-meta-werks-0.1.1.jar",
        in_file,
        out_file,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(in_file + " did not work. ")
        return
    return result.stdout.strip()

def ast_creator_task():
    repositories = get_repositories()
    for repository in repositories:
        commits = get_repository_commits(repository["id"])
        for commit in commits:
            commit_files = get_repository_commit_files(commit["repo_id"], commit["commit_hash"])
            for commit_file_info in commit_files:
                if is_java_file(commit_file_info["file_name"]):
                    in_file_path = commit_file_info["file_path"]
                    out_file_path = os.path.join(commit_file_info["dir_name"], get_ast_for_java_source_file(commit_file_info["file_name"]))
                    ast_creator(in_file_path, out_file_path)
                    print("ast created for file " + str(commit_file_info))


if __name__ == "__main__":
    ast_creator_task()
