import hashlib


def get_compilation_unit_obj(file_name):
    return {
        "type": "compilation-unit",
        "identifier": file_name,
        "id": f"cu:{file_name}",
        "uid": f"cu:{file_name}",
        "children": [],
    }


def get_package_obj(parent_uid, p_node):
    package_name = build_name(p_node["name"])
    return {
        "type": "package",
        "identifier": package_name,
        "id": f"p:{package_name}",
        "uid": f"{parent_uid}/p:{package_name}",
        "children": [],
    }


def get_import_obj(parent_uid, imp_node):
    import_name = build_name(imp_node["name"])
    return {
        "type": "import",
        "identifier": import_name,
        "id": f"im:{import_name}",
        "uid": f"{parent_uid}/im:{import_name}",
    }


def get_class_obj(parent_uid, c_node):
    class_name = c_node["name"]["identifier"]
    return {
        "type": "class",
        "identifier": class_name,
        "id": f"c:{class_name}",
        "uid": f"{parent_uid}/c:{class_name}",
        "children": [],
    }


def get_method_obj(parent_uid, m_node):
    method_name = m_node["name"]["identifier"]
    fingerprint = generate_unique_hash(get_condensed_method_object(m_node))
    return {
        "type": "method",
        "identifier": method_name,
        "id": f"m:{method_name}",
        "uid": f"{parent_uid}/m:{method_name}",
        "fingerprint": fingerprint,
        "children": [],
    }


def get_identifier_obj(parent_uid, id_node):
    identifier_name = id_node["name"]["identifier"]
    return {
        "type": "identifier",
        "identifier": identifier_name,
        "id": f"i:{identifier_name}",
        "uid": f"{parent_uid}/i:{identifier_name}",
    }


def get_comment_obj(parent_uid, co_node):
    comment = co_node["comment"]["content"]
    comment_hash = generate_unique_hash(co_node)
    return {
        "type": "comment",
        "identifier": comment_hash,
        "id": f"cm:{comment_hash}",
        "uid": f"{parent_uid}/cm:{comment_hash}",
        "content": comment,
    }


def build_name(node):
    if "qualifier" in node:
        return build_name(node.get("qualifier")) + "." + node.get("identifier")
    else:
        return node.get("identifier")


def get_condensed_method_object(m_node, sort=True):
    def accept_visitor(value, parent, key, level):
        if key == "range" and isinstance(value, dict) and "beginLine" in value:
            return False
        if key == "tokenRange" and isinstance(value, dict) and "beginToken" in value:
            return False
        # ignore empty arrays
        if isinstance(value, list) and not value:
            return False
        # ignore imports
        if key == "imports" and isinstance(value, list):
            return False
        return True


def generate_unique_hash(condensed_method_object):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(str(condensed_method_object).encode("utf-8"))
    unique_hash = sha256_hash.hexdigest()
    pass
    return unique_hash
