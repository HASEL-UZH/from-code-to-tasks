import hashlib
import os

from src.ast_meta_generation.meta_ast_utils import filter_json

def meta_ast_creator(file_name, input_json):
    package_name = get_package_name(input_json)
    output_json = {
        "type": "compilation-unit",
        "identifier": file_name,
        "id": f"cu:{package_name}.{file_name}",
        "uid": f"cu:{package_name}.{file_name}",
        "pid": package_name,
        "children": [],
    }

    for i, class_type in enumerate(input_json.get("types")):
        types = input_json.get("types")[i]
        node_type = types.get("!").rsplit(".", 1)[-1]
        if node_type == "ClassOrInterfaceDeclaration":
            class_name = input_json.get("types")[i].get("name").get("identifier")
            output_json["children"].append(
                {
                    "type": "class",
                    "id": f"c:{class_name}",
                    "uid": f"{output_json['uid']}/c:{class_name}",
                    "identifier": class_name,
                    "children": [],
                }
            )
        else:
            continue
        for j, method_member in enumerate(input_json.get("types")[i].get("members")):
            member = input_json.get("types")[i].get("members")[j]
            node_type = member.get("!").rsplit(".", 1)[-1]
            if node_type == "MethodDeclaration":
                method_name = (
                    input_json.get("types")[i]
                    .get("members")[j]
                    .get("name")
                    .get("identifier")
                )
                condensed_method_object = get_condensed_method_object(member)
                output_json["children"][i]["children"].append(
                    {
                        "type": "method",
                        "id": f"m:{method_name}",
                        "uid": f"{output_json['children'][i]['uid']}/m:{method_name}",
                        "identifier": method_name,
                        "fingerprint": str(
                            generate_unique_hash(condensed_method_object)
                        ),
                    }
                )
            else:
                continue
    return output_json


def get_condensed_method_object(method_object, sort=True):
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
    result = filter_json(method_object, accept_visitor, sort)
    return result

def get_package_name(json_obj):
    package_declaration = json_obj.get("packageDeclaration")
    if package_declaration:
        name = package_declaration.get("name")
        identifier = name.get("identifier")
        qualifier = name.get("qualifier")
        while qualifier:
            identifier = qualifier.get("identifier") + "." + identifier
            qualifier = qualifier.get("qualifier")
        return identifier


def generate_unique_hash(condensed_method_object):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(str(condensed_method_object).encode("utf-8"))
    unique_hash = sha256_hash.hexdigest()
    pass
    return unique_hash