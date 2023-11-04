import os
import subprocess

from src.object_factory import ObjectFactory, get_resource_id
from src.object_store import db


def _create_ast(in_file, out_file):
    print(f"create AST for {in_file}")
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
    java_resources = db.find_many({
        "classifier": "resource",
        "type": "java"
    })
    java_resources_2 = db.find_resources({"type": "java"})
    java_resources_3 = db.find_resources(lambda d: d.get("type") == "java" )

    for java_source_resource in java_resources:
        commit = db.find_object(java_source_resource.get("@container"))
        if ObjectFactory.is_commit(commit):
            ast_target_resource = ObjectFactory.resource(commit, {
                "name": java_source_resource.get("name"),
                "type": "json",
                "kind": "ast",
                "version": java_source_resource.get("version"),
            })
            source_file = db.get_resource_path(java_source_resource)
            target_file = db.get_resource_path(ast_target_resource)
            _create_ast(source_file, target_file)
    pass


if __name__ == "__main__":
    create_ast_task()
