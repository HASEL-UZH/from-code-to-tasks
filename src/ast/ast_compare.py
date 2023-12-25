from src.ast.ast_utils import get_parent_uid, create_ast_map


def compare_ast(before, after):
    changes = []

    left = create_ast_map(before)
    right = create_ast_map(after)

    for key, left_node in left.items():
        if key in right:
            right_node = right[key]
            left_node["children"] = []
            right_node["children"] = []
            change_type = (
                "modify"
                if (
                    left_node.get("fingerprint", None)
                    != right_node.get("fingerprint", None)
                )
                or (
                    left_node.get("composite_fingerprint", None)
                    != right_node.get("composite_fingerprint", None)
                )
                or (
                    left_node.get("body_fingerprint", None)
                    != right_node.get("body_fingerprint", None)
                )
                else "none"
            )
            change = {
                "uid": key,
                "type": left_node["type"],
                "change": {
                    "type": change_type,
                    "before": left_node,
                    "after": right_node,
                },
                "children": [],
            }
            changes.append(change)
    for change in changes:
        del left[change["uid"]]
        del right[change["uid"]]

    for key, left_node in left.items():
        if key not in right:
            change = {
                "uid": key,
                "type": left_node["type"],
                "change": {
                    "type": "delete",
                    "before": left_node,
                    "after": None,
                },
                "children": [],
            }
            changes.append(change)
    for key, right_node in right.items():
        if key not in left:
            change = {
                "uid": key,
                "type": right_node["type"],
                "change": {
                    "type": "add",
                    "before": None,
                    "after": right_node,
                },
                "children": [],
            }
            changes.append(change)

    for i, change in enumerate(changes):
        change = change["change"]
        if change.get("before") and change.get("after"):
            if change["before"]["type"] == "compilation-unit":
                if change["before"]["filename"] != change["after"]["filename"]:
                    change["rename"] = {
                        "before": change["before"]["filename"],
                        "after": change["after"]["filename"],
                    }
                if change["before"]["package"] != change["after"]["package"]:
                    change["move"] = {
                        "before": change["before"]["package"],
                        "after": change["after"]["package"],
                    }
            elif change["before"]["type"] == "class":
                if change["before"]["identifier"] != change["after"]["identifier"]:
                    change["rename"] = {
                        "before": change["before"]["identifier"],
                        "after": change["after"]["identifier"],
                    }
        if change.get("before"):
            if change["before"]["type"] == "comment" and change["type"] == "delete":
                parent = change["before"]["uid"].rsplit("/", 1)[0]
                matching_object = next(
                    (
                        obj
                        for obj in changes
                        if (
                            obj.get("change", {}).get("after", {}) is not None
                            and obj.get("change", {})
                            .get("after", {})
                            .get("uid", "")
                            .rsplit("/", 1)[0]
                            == parent
                            and obj.get("type") == "comment"
                            and obj.get("change", {}).get("type") == "add"
                        )
                    ),
                    None,
                )
                if matching_object is not None:
                    removed_item = changes.pop(i)
                    matching_object["change"]["type"] = "modify"
    return changes


def build_change_tree(changes):
    lookup = {}
    root = None
    for change in changes:
        lookup[change["uid"]] = change
    for i, change in enumerate(changes):
        pid = get_parent_uid(change["uid"])
        parent = lookup.get(pid)
        if parent is not None:
            parent["children"].append(change)
        else:
            if root is not None:
                pass
                raise Exception
            root = change
    return root
