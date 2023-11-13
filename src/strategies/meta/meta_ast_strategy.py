from src.ast.meta_ast_node_creator import (
    get_identifier_object,
    get_method_object,
    get_class_object,
    get_output_json,
    get_import_object,
)
from src.ast.meta_ast_utils import filter_json, traverse_json_with_context


def create_meta_ast(file_name, input_json, opts=None):
    options = get_options(opts)
    package_name = get_package_name(input_json)
    output_json = get_output_json(package_name, file_name)

    # TODO differentiate if interface
    for i, class_type in enumerate(input_json.get("types")):
        node_type = input_json.get("types")[i]["!"]
        if node_type == "com.github.javaparser.ast.body.ClassOrInterfaceDeclaration":
            class_node = input_json.get("types")[i]
            class_name = class_node.get("name").get("identifier")
            output_json["children"].append(
                get_class_object(output_json["uid"], class_name)
            )
        else:
            continue

        if options["methods"]:
            for j, method_member in enumerate(
                input_json.get("types")[i].get("members")
            ):
                node_type = input_json.get("types")[i].get("members")[j]["!"]
                if node_type == "com.github.javaparser.ast.body.MethodDeclaration":
                    method_node = input_json.get("types")[i].get("members")[j]
                    method_name = method_node.get("name").get("identifier")
                    condensed_method_object = get_condensed_method_object(method_node)
                    output_json["children"][i]["children"].append(
                        get_method_object(
                            output_json["children"][i]["uid"],
                            method_name,
                            condensed_method_object,
                        )
                    )
                else:
                    continue

                if options["identifiers"]:
                    method_identifiers = set()
                    context = {"set": method_identifiers}
                    identifiers = traverse_json_with_context(
                        method_node, identifier_enter_visitor, context=context
                    )["set"]
                    for identifier in identifiers:
                        output_json["children"][i]["children"][j]["children"].append(
                            get_identifier_object(
                                output_json["children"][i]["children"][j]["uid"],
                                identifier,
                            )
                        )

                # TODO COMMENTS

    if options["imports"]:
        imports = [
            get_import_name(import_name.get("name"))
            for import_name in input_json.get("imports")
        ]
        for import_name in imports:
            output_json["children"].append(
                get_import_object(output_json["uid"], import_name)
            )

    return output_json


def get_options(opts):
    default_opts = {
        "imports": True,
        "methods": True,
        "identifiers": True,
        "comments": True,
    }
    options = {**default_opts, **(opts or {})}
    return options


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


def get_import_name(import_data):
    if "qualifier" in import_data:
        return (
            get_import_name(import_data.get("qualifier"))
            + "."
            + import_data.get("identifier")
        )
    else:
        return import_data.get("identifier")


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


def comment_enter_visitor(value, parent, parent_key, level, context):
    pass


def identifier_enter_visitor(value, parent, parent_key, level, context):
    if value == "com.github.javaparser.ast.body.VariableDeclarator":
        identifier_name = parent.get("name").get("identifier")
        print(f" {' ' * level} {identifier_name}")
        context["set"].add(identifier_name)
        return context
