import json
import os

from src.ast.ast_compare import compare_ast, build_change_tree
from src.ast.ast_utils import create_ast_map, traverse_ast, traverse_ast_postorder
from src.core.utils import hash_string, hash_object


def prepare_ast(commit_change, meta_ast, state):
    flat_meta_ast = create_ast_map(meta_ast)
    path = commit_change["old_path"] if state == "before" else commit_change["new_path"]
    cu = meta_ast
    for key, node in flat_meta_ast.items():
        if node["type"] == "package":
            cu["package"] = node["identifier"]
        elif node["type"] == "import":
            node["fingerprint"] = hash_string(node["identifier"])
        elif node["type"] == "comment":
            node["fingerprint"] = hash_string(node["identifier"])
        elif node["type"] == "identifier":
            node["fingerprint"] = hash_string(node["identifier"])
        elif node["type"] == "method":
            node["fingerprint"] = hash_string(node["identifier"])
        elif node["type"] == "class":
            class_name = os.path.basename(path).replace(".java", "")
            node["is_main_class"] = class_name == node["identifier"]
            node["class_name"] = class_name
            if node["identifier"] != cu["identifier"] and node["is_main_class"]:
                # Rename
                uid_old = node["uid"]
                uid_new = "/".join([uid_old.split("/")[0], "c:" + cu["identifier"]])
                node["uid"] = uid_new

                def patch_visitor(node, parent, level):
                    prev_uid = uid_old + "/"
                    if node["uid"].startswith(prev_uid):
                        node["uid"] = uid_new + node["uid"][len(prev_uid) - 1 :]

                traverse_ast(node, patch_visitor)

            node["fingerprint"] = hash_object(
                {
                    key: node[key]
                    for key in ["identifier", "class_name", "is_main_class"]
                }
            )

    def fingerprint_visitor(node, parent, level):
        if node.get("children"):
            fingerprint_list = [
                obj["composite_fingerprint"] for obj in node["children"]
            ]
            node["composite_fingerprint"] = hash_string(
                ",".join(sorted(fingerprint_list))
            )
        else:
            print(node["uid"])
            node["composite_fingerprint"] = node.get("fingerprint", "undefined")

    cu["filename"] = os.path.basename(path)
    cu["fingerprint"] = hash_object(
        {key: cu[key] for key in ["identifier", "filename", "package"]}
    )
    cu["children"] = [item for item in cu["children"] if item.get("type") != "package"]
    traverse_ast_postorder(cu, fingerprint_visitor)
    pass


def create_ast_change_model(json_dict, commit):
    pull_request = commit["pull_request"]
    commit_changes = {obj["filename"]: obj for obj in commit["changes"]}
    commit_change_object = {
        "pr": {"text": pull_request},
        "code": {"text": "", "details": []},
    }
    for file_name, change_tuple in json_dict.items():
        before_meta_ast_json, after_meta_ast_json = change_tuple
        before_meta_ast = json.loads(before_meta_ast_json)
        after_meta_ast = json.loads(after_meta_ast_json)
        commit_change = commit_changes[f"{file_name}.java"]
        prepare_ast(commit_change, before_meta_ast, "before")
        prepare_ast(commit_change, after_meta_ast, "after")
        ast_compare_flat = compare_ast(before_meta_ast, after_meta_ast)
        try:
            ast_compare_tree = build_change_tree(ast_compare_flat)
        except:
            ast_compare_tree = {}
            pass
        commit_change_object["code"]["details"].append(ast_compare_tree)
    return commit_change_object
