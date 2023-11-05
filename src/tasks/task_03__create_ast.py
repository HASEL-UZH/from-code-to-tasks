import os
import subprocess

from src.object_factory import ObjectFactory
from src.object_store import db
from src.utils.profiler import Profiler

def create_ast_task():
    print("create_ast_task started")

    count = 0
    profiler = Profiler()

    java_resources = db.find_many({"classifier": "resource", "type": "java"})
    for java_source_resource in java_resources:
        commit = db.find_object(java_source_resource.get("@container"))
        count += 1
        if count % 1000 == 0:
            profiler.checkpoint(f"AST resources: {count} of total: {len(java_resources)}")

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

    # }
    profiler.checkpoint(f"create_ast_task done: {count}")
    db.invalidate()
# }


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



if __name__ == "__main__":
    create_ast_task()
