from src.object_factory import ObjectFactory
from src.object_store import db
from src.strategies.meta_ast.default_meta_ast_strategy import meta_ast_creator


def create_meta_ast_task():
    default_strategy = {
        "identifier": "default",
        "meta_ast_creator": meta_ast_creator,
    }

    ast_resources = db.find_resources({"kind": "ast", "type": "json"})
    for ast_resource in ast_resources:
        commit = db.find_object(ast_resource.get("@container"))
        if ObjectFactory.is_commit(commit):
            ast_meta_target_resource = ObjectFactory.resource(commit, {
                "name": ast_resource.get("name"),
                "type": "json",
                "kind": "meta-ast",
                "version": ast_resource.get("version"),
            })
            ast_input_json = db.load_resource(ast_resource)
            meta_ast_output_json = meta_ast_creator(ast_resource["name"], ast_input_json)
            ast_meta_target_resource["content"]=meta_ast_output_json
            db.save_resource(ast_meta_target_resource)


if __name__ == "__main__":
    create_meta_ast_task()
