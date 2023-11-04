import os

from src.ast_compare.ast_compare import compare_ast, build_change_tree
from src.ast_compare.ast_compare_text import generate_change_text_for_file
from src.object_factory import ObjectFactory
from src.repository_manager import get_repositories, get_repository_commits, get_repository_commit_files
from src.object_store import db
from src.utils.utils import group_by


def build_commit_change_object(json_dict, pull_request):
    commit_compare_text = ""
    commit_change_object = {
        "pr": {"text": pull_request},
        "code": {"text": "", "details": []},
    }
    for file_name, change_tuple in json_dict.items():
        before_meta_ast, after_met_ast = change_tuple
        ast_compare_flat = compare_ast(before_meta_ast, after_met_ast)
        try:
            ast_compare_tree = build_change_tree(ast_compare_flat)
        except:
            ast_compare_tree = {}
            pass
        commit_change_object["code"]["details"].append(ast_compare_tree)
        ast_file_change_text = generate_change_text_for_file(
            file_name, ast_compare_tree
        )
        commit_compare_text += ast_file_change_text
        commit_change_object["code"]["text"] = commit_compare_text
    return commit_change_object


def change_model_creator_task():
    meta_ast_resources = db.find_resources({"kind": "meta-ast", "type": "json"})
    commit_groups = group_by(meta_ast_resources, "@container")
    for commit_key, commit_resources in commit_groups.items():
        commit = db.find_object(commit_key)
        resource_dict = {}
        resource_groups = group_by(commit_resources, "name")
        for resource_key, file_resources in resource_groups.items():
            resource_before = db.find_one({"version": "before"}, file_resources)
            resource_after = db.find_one({"version": "after"}, file_resources)
            meta_before = db.load_resource(resource_before)
            meta_after = db.load_resource(resource_after)
            resource_dict[resource_key] = (meta_before, meta_after)
        change_object = build_commit_change_object(resource_dict, commit["pull_request"])
        change_resource = ObjectFactory.resource(commit, {
            "name": "summary",
            "type": "json",
            "kind": "change",
            "version": None,
            "content": change_object,
            "strategy": {
                "terms": "default"
            }
        })
        db.save_resource(change_resource)
    # }
# }

if __name__ == "__main__":
    change_model_creator_task()
