import os
import subprocess
from typing import Iterable

from src.core.profiler import Profiler
from src.store.mdb_store import db
from src.store.object_factory import ObjectFactory
from src.tasks.pipeline_context import PipelineContext, DEFAULT_PIPELINE_CONTEXT

AST_PARSER_JAR_V1 = "./bin/ast-meta-werks-0.1.1.jar"
AST_PARSER_JAR_V2 = "./bin/ast-meta-werks-0.2.4.jar"


def create_ast_task(context: PipelineContext):
    print("create_ast_task started")
    db.delete_resources_where(context.create_resource_criteria({"kind": "ast"}))
    count = 0
    profiler = Profiler()
    criteria = context.create_resource_criteria(
        {
            "kind": "source",
        }
    )
    java_resources = db.find_resources(criteria)
    create_ast_task_multi(java_resources, profiler, mode="parallel")

    profiler.checkpoint(f"create_ast_task done: {count}")


def create_ast_task_multi(java_resources: Iterable, profiler, mode="parallel"):
    print("execution strategy: multi")
    profiler = Profiler("create_ast_task_multi")
    conversions = []
    for java_source_resource in java_resources:
        commit = db.find_object(java_source_resource.get("@container"))
        if ObjectFactory.is_commit(commit):
            ast_target_resource = ObjectFactory.resource(
                commit,
                {
                    "name": java_source_resource.get("name"),
                    "type": "json",
                    "kind": "ast",
                    "version": java_source_resource.get("version"),
                },
            )
            source_file = db.get_resource_path(java_source_resource)
            target_file = db.get_resource_path(ast_target_resource)
            db.save_resource(ast_target_resource, commit)
            conversions.append({"in_file": source_file, "out_file": target_file})
            if len(conversions) % 100 == 0:
                profiler.debug(f"Count: {len(conversions)}")

    temp_file_path = db.generate_tmp_file()
    with open(temp_file_path, "w") as file:
        for conversion in conversions:
            file.write(f"{conversion['in_file']},{conversion['out_file']}\n")

    profiler.info("Invoke java AST parser")
    try:
        _create_multi_ast(temp_file_path, mode=mode)
    except Exception as e:
        print(f"Execution failed:  " + e)
    finally:
        if os.path.exists(temp_file_path):
            pass
    profiler.info("done")


def create_ast_task_single(java_resources, profiler):
    print("execution strategy: single")
    count = 0
    for java_source_resource in java_resources:
        commit = db.find_object(java_source_resource.get("@container"))
        count += 1
        if count % 1000 == 0:
            profiler.checkpoint(
                f"AST resources: {count} of total: {len(java_resources)}"
            )
        if ObjectFactory.is_commit(commit):
            ast_target_resource = ObjectFactory.resource(
                commit,
                {
                    "name": java_source_resource.get("name"),
                    "type": "json",
                    "kind": "ast",
                    "version": java_source_resource.get("version"),
                },
            )
            source_file = db.get_resource_path(java_source_resource)
            target_file = db.get_resource_path(ast_target_resource)
            _create_ast(source_file, target_file)


def _create_multi_ast(temp_file_path, mode="serial"):
    print(f"create AST for batch file {temp_file_path}")
    command = [
        "java",
        "-jar",
        AST_PARSER_JAR_V2,
        "--mode",
        mode,
        "--file",
        temp_file_path,
    ]
    print(command)
    result = subprocess.run(command, capture_output=False, text=True)
    if result.returncode != 0:
        print(temp_file_path + " did not work. ")
        return
    if result.stdout:
        return result.stdout.strip()
    else:
        return None


def _create_ast(in_file, out_file):
    print(f"create AST for {in_file}")
    command = [
        "java",
        "-jar",
        AST_PARSER_JAR_V1,
        in_file,
        out_file,
    ]
    result = subprocess.run(command, capture_output=False, text=True)
    if result.returncode != 0:
        print(in_file + " did not work. ")
        return
    if result.stdout:
        return result.stdout.strip()
    else:
        return None


if __name__ == "__main__":
    create_ast_task(DEFAULT_PIPELINE_CONTEXT)
