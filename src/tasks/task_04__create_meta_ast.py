from src.core.profiler import Profiler
from src.store.object_factory import ObjectFactory
from src.store.object_store import db
from src.strategies.meta_ast.default_meta_ast_strategy import meta_ast_creator


def create_meta_ast_task():
    print("create_meta_ast_task started")

    meta_ast_resources = db.find_resources({"kind": "meta-ast", "type": "json"})
    db.delete_resources(meta_ast_resources)

    ast_resources = db.find_resources({"kind": "ast", "type": "json"})

    count = 0
    profiler = Profiler()

    for ast_resource in ast_resources:
        commit = db.find_object(ast_resource.get("@container"))
        if ObjectFactory.is_commit(commit):
            count += 1
            if count % 1000 == 0:
                profiler.checkpoint(f"Meta-AST resources: {count} of total: {len(ast_resources)}")

            ast_meta_target_resource = ObjectFactory.resource(commit, {
                "name": ast_resource.get("name"),
                "type": "json",
                "kind": "meta-ast",
                "version": ast_resource.get("version"),
                "strategy": {
                    "meta": "default"
                }
            })
            ast_input_json = db.get_resource_content(ast_resource)
            meta_ast_output_json = meta_ast_creator(ast_resource["name"], ast_input_json)
            ast_meta_target_resource["content"]=meta_ast_output_json
            db.save_resource(ast_meta_target_resource, invalidate=False)
    # }
    profiler.checkpoint(f"create_meta_ast_task done: {count}")
    db.invalidate()



if __name__ == "__main__":
    create_meta_ast_task()
