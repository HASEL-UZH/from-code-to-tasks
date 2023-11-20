from src.ast.ast_utils import create_ast_map
from src.store.mdb_store import db


def get_change_type(change_obj):
    if change_obj == "compilation-unit":
        return "file"
    elif change_obj == "package":
        return "package"
    elif change_obj == "import":
        return "import"
    elif change_obj == "comment":
        return "comment"
    elif change_obj == "class":
        return "class"
    elif change_obj == "method":
        return "method"
    elif change_obj == "identifier":
        return "identifier"


def get_change_context(change_obj):
    context_str = ""
    obj_uid = change_obj["uid"]
    context_uids = obj_uid.split("/")[:-1]
    for context_uid in context_uids:
        uid_parts = context_uid.split(":")
        if uid_parts[0] == "cu":
            context_str += f"in file {uid_parts[1]} "
        if uid_parts[0] == "c":
            context_str += f"in class {uid_parts[1]} "
        if uid_parts[0] == "m":
            context_str += f"in method {uid_parts[1]} "
    return context_str.rstrip()


def create_meta_ast_text(resource):
    resource_content = db.get_resource_content(resource)
    meta_ast_text = ""
    for cu_node in resource_content["code"]["details"]:
        flat_changes = create_ast_map(cu_node)
        filtered_changes = {
            key: value
            for key, value in flat_changes.items()
            if value["change"]["type"] != "none"
        }
        for change_key, change_obj in filtered_changes.items():
            text_per_change = ""
            change_type = change_obj["change"]["type"]

            # RENAME
            if "rename" in change_obj.get("change", {}):
                text_per_change += f'Rename {get_change_type(change_obj["type"])} from {change_obj["change"]["rename"]["before"]} to {change_obj["change"]["rename"]["after"]}. '

            # MOVE
            if "move" in change_obj.get("change", {}):
                text_per_change += f'Move {get_change_type(change_obj["type"])} {change_obj["change"]["after"]["filename"].replace(".java", "")}  from {change_obj["change"]["move"]["before"]} to {change_obj["change"]["move"]["after"]}. '

            # ADD
            if change_type == "add":
                if change_obj["type"] == "comment":
                    text_per_change += f'Add {get_change_type(change_obj["type"])}  {change_obj["change"]["after"]["content"]} {get_change_context(change_obj)}. '
                else:
                    text_per_change += f'Add {get_change_type(change_obj["type"])} {change_obj["change"]["after"]["identifier"]} {get_change_context(change_obj)}. '
            # DELETE
            elif change_type == "delete":
                if change_obj["type"] == "comment":
                    text_per_change += f'Delete {get_change_type(change_obj["type"])}  {change_obj["change"]["before"]["content"]} {get_change_context(change_obj)}. '
                else:
                    text_per_change += f'Delete {get_change_type(change_obj["type"])} {change_obj["change"]["before"]["identifier"]} {get_change_context(change_obj)}. '
            # MODIFY
            elif (
                change_type == "modify"
                and "rename" not in change_obj.get("change", {})
                and "move" not in change_obj.get("change", {})
            ):
                if change_obj["type"] == "comment":
                    text_per_change += f'Modify {get_change_type(change_obj["type"])}  {change_obj["change"]["after"]["content"]} {get_change_context(change_obj)}. '
                else:
                    text_per_change += f'Modify {get_change_type(change_obj["type"])} {change_obj["change"]["before"]["identifier"]} {get_change_context(change_obj)}. '
            meta_ast_text += text_per_change
    return meta_ast_text.rstrip()
