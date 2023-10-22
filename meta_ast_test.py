import hashlib
import json
import re


def meta_ast_test():
    folder_path = "AstMetaWorkspace/data/out/MultipleMethod.ast.json"
    with open(folder_path, 'r') as json_file:
        input_json = json.load(json_file)
    file = "Example.ast.json"
    file_name = re.sub(r'\..*', '', file)
    package_name = get_package_name(input_json)

    output_json = {
        "type": "compilation-unit",
        "identifier": file_name,
        "children": [
        ]}

    output_json["children"].append({
        "type": "package",
        "identifier": package_name,
        "children": [
        ]})

    for i, class_type in enumerate(input_json.get("types")):
        output_json["children"][0]["children"].append({
        "type": "class",
        "identifier": input_json.get("types")[i].get("name").get("identifier"),
        "children": []
        })
        for j,method_member in enumerate(input_json.get("types")[i].get("members")):
            output_json["children"][0]["children"][i]["children"].append({
                "type": "method",
                "identifier": input_json.get("types")[i].get("members")[j].get("name").get("identifier"),
                "fingerprint": str(generate_unique_hash(input_json.get("types")[i].get("members")[j]))
            })
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
    sha256_hash.update(str(input_json).encode('utf-8'))
    unique_hash = sha256_hash.hexdigest()
    return unique_hash


if __name__ == "__main__":
    print(meta_ast_test())
