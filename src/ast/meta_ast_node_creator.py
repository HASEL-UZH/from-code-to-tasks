import hashlib


def get_output_json(package_name, file_name):
    output_json = {
        "type": "compilation-unit",
        "identifier": file_name,
        "id": f"cu:{package_name}.{file_name}",
        "uid": f"cu:{package_name}.{file_name}",
        "pid": package_name,
        "children": [],
    }
    return output_json


def get_class_object(parent_uid, class_name):
    return {
        "type": "class",
        "id": f"c:{class_name}",
        "uid": f"{parent_uid}/c:{class_name}",
        "identifier": class_name,
        "children": [],
    }


def get_method_object(parent_uid, method_name, condensed_method_object):
    return {
        "type": "method",
        "id": f"m:{method_name}",
        "uid": f"{parent_uid}/m:{method_name}",
        "identifier": method_name,
        "fingerprint": str(generate_unique_hash(condensed_method_object)),
        "children": [],
    }


def get_identifier_object(parent_uid, identifier_name):
    return {
        "type": "identifier",
        "id": f"i:{identifier_name}",
        "uid": f"{parent_uid}/i:{identifier_name}",
        "identifier": identifier_name,
    }


def get_comment_object(parent_uid, comment):
    comment_hash = generate_unique_hash(comment)
    return {
        "type": "comment",
        "id": f"cm:{comment_hash}",
        "uid": f"{parent_uid}/cm:{comment_hash}",
        "identifier": comment_hash,
    }


def get_import_object(parent_uid, import_name):
    return {
        "type": "import",
        "id": f"im:{import_name}",
        "uid": f"{parent_uid}/im:{import_name}",
        "identifier": import_name,
    }


def generate_unique_hash(condensed_method_object):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(str(condensed_method_object).encode("utf-8"))
    unique_hash = sha256_hash.hexdigest()
    pass
    return unique_hash
