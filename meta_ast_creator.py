import hashlib
import json
import os
import re


def ast_file_iterator():
    folder_path = (
        "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    )

    folder_path = os.path.join(os.path.dirname(__file__), folder_path)

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(("after_ast.json", "before_ast.json")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as json_file:
                        input_json = json.load(json_file)
                        out_file_name = re.sub(r"ast", "meta_ast", file)
                        out_folder = os.path.join(root, out_file_name)
                        meta_ast = meta_ast_creator(input_json)
                        with open(out_folder, "w") as json_file:
                            json.dump(meta_ast, json_file, indent=4)


def meta_ast_creator(input_json):
    # TODO fix
    file = "Example.ast.json"
    file_name = re.sub(r"\..*", "", file)
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
                output_json["children"][i]["children"].append(
                    {
                        "type": "method",
                        "id": f"m:{method_name}",
                        "uid": f"{output_json['children'][i]['uid']}/m:{method_name}",
                        "identifier": method_name,
                        "fingerprint": str(
                            generate_unique_hash(
                                input_json.get("types")[i].get("members")[j]
                            )
                        ),
                    }
                )
            else:
                continue
    print(output_json)
    return output_json


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


def generate_unique_hash(input_json):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(str(input_json).encode("utf-8"))
    unique_hash = sha256_hash.hexdigest()
    return unique_hash


if __name__ == "__main__":
    ast_file_iterator()
