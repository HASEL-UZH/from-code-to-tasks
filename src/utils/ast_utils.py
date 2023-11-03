def traverse_ast(root, visitor_fn):
    def _traverse(node, parent, level):
        visitor_fn(node, parent, level)
        for child in node.get("children", []):
            _traverse(child, node, level + 1)

    _traverse(root, None, 0)


def is_compilation_unit(node):
    return node.get("type") == "compilation-unit"


def is_class(node):
    return node.get("type") == "class"


def is_method(node):
    return node.get("type") == "method"


def create_ast_map(root):
    map = {}

    def visitor(node, parent, level):
        map[node["uid"]] = node

    if root is not None:
        traverse_ast(root, visitor)
    return map


def get_parent_uid(uid):
    pid = "/".join(uid.split("/")[:-1])
    pass
    return pid if len(pid) > 0 else None


def get_name_from_uid(uid):
    name = uid.rsplit(":", 1)[-1].strip()
    pass
    return name
