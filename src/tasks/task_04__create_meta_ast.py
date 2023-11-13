from src.core.profiler import Profiler
from src.store.object_factory import ObjectFactory
from src.store.object_store import db
from src.strategies.meta.meta_ast_strategy import create_meta_ast


def create_meta_ast_task():

    # TODO add meta code strategy
    # TODO add meta diff text strategy

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
                profiler.checkpoint(
                    f"Meta-AST resources: {count} of total: {len(ast_resources)}"
                )

            ast_meta_target_resource = ObjectFactory.resource(
                commit,
                {
                    "name": ast_resource.get("name"),
                    "type": "json",
                    "kind": "meta-ast",
                    "version": ast_resource.get("version"),
                    "strategy": {"meta": ""},
                },
            )
            ast_input_json = db.get_resource_content(ast_resource)

            for imports in [True, False]:
                for methods in [True, False]:
                    for identifiers in [True, False]:
                        for comments in [True, False]:
                            options = {
                                "imports": imports,
                                "methods": methods,
                                "identifiers": identifiers,
                                "comments": comments,
                            }

                            option_string = f"im:{imports}, me:{methods}, id:{identifiers}, co:{comments}"
                            meta_ast = create_meta_ast(
                                ast_resource["name"], ast_input_json, options
                            )
                            print(f"Options: {options}, Result AST: {meta_ast}")
                            # TODO validate
                            ast_meta_target_resource["strategy"]["meta"] = option_string
                            ast_meta_target_resource["content"] = meta_ast
                            db.save_resource(ast_meta_target_resource, invalidate=False)

    profiler.checkpoint(f"create_meta_ast_task done: {count}")
    db.invalidate()


if __name__ == "__main__":
    create_meta_ast_task()
