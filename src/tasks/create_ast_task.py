import os
import subprocess

from src.object_store import db


def _create_ast(in_file, out_file):
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

def create_ast_task():
    resources = db.get_resources()
    for resource in resources:
        content = db.load_resource(resource)
        content2 = db.load_resource(resource)
        pass
    java_resources = [obj for obj in resources if obj["type"] == "java"]
    pass
    # FIXME


if __name__ == "__main__":
    create_ast_task()
