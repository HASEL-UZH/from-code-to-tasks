import json

from src.core.profiler import Profiler
from src.core.logger import log
from src.store.object_factory import ObjectFactory
from src.store.mdb_store import db
from src.strategies.meta.meta_ast_strategy import (
    MetaAstBuilder,
    traverse_json_structure,
)


def get_ast_meta_resource(ast_resource, commit, ast_meta_strategy, content):
    return ObjectFactory.resource(
        commit,
        {
            "name": ast_resource.get("name"),
            "type": "json",
            "kind": "meta",
            "version": ast_resource.get("version"),
            "strategy": {"meta": ast_meta_strategy},
            "content": content,
        },
    )


def create_meta_ast_task():
    print("create_meta_ast_task started")
    db.delete_resources_where({"kind": "meta", "type": "json"})
    ast_resources = list(db.find_resources({"kind": "ast", "type": "json"}))
    count = 0
    profiler = Profiler("create_meta_ast_task")

    for ast_resource in ast_resources:
        commit = db.find_object(ast_resource.get("@container"))
        if ObjectFactory.is_commit(commit):
            count += 1
            if count % 100 == 0:
                profiler.debug(f"AST resources: {count} of total: {len(ast_resources)}")

            ast_input_json = db.get_resource_content(ast_resource)

            # ast_sm - include methods
            ast_builder_sm = MetaAstBuilder(
                ast_resource["name"],
                {
                    "imports": False,
                    "identifiers": False,
                    "comments": False,
                },
            )
            # ast_md - include methods, comments
            ast_builder_md = MetaAstBuilder(
                ast_resource["name"],
                {
                    "imports": False,
                    "identifiers": False,
                },
            )
            # ast_lg - include, methods, comments, identifiers, imports
            ast_builder_lg = MetaAstBuilder(ast_resource["name"])

            traverse_json_structure(ast_input_json, ast_builder_sm)
            traverse_json_structure(ast_input_json, ast_builder_md)
            traverse_json_structure(ast_input_json, ast_builder_lg)

            ast_sm = ast_builder_sm.get_root()
            ast_md = ast_builder_md.get_root()
            ast_lg = ast_builder_lg.get_root()

            ast_meta_target_resource_sm = get_ast_meta_resource(
                ast_resource, commit, "ast-sm", ast_sm
            )
            db.save_resource(ast_meta_target_resource_sm, commit)

            ast_meta_target_resource_md = get_ast_meta_resource(
                ast_resource, commit, "ast-md", ast_md
            )
            db.save_resource(ast_meta_target_resource_md, commit)

            ast_meta_target_resource_lg = get_ast_meta_resource(
                ast_resource, commit, "ast-lg", ast_lg
            )
            db.save_resource(ast_meta_target_resource_lg, commit)

    profiler.info(f"create_meta_ast_task done: {count}")


if __name__ == "__main__":
    create_meta_ast_task()
