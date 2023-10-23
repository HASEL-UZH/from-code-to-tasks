import json

from ast_utils import traverse_ast, is_compilation_unit, is_class, is_method


def generate_change_text_for_file(file_name):
    with open(file_name, "r") as file:
        change_model = json.load(file)
        root = change_model
        generated_text = ""

        def generate(node, parent, level):
            nonlocal generated_text
            text = generate_change_text(node, parent, level)
            generated_text += text

        traverse_ast(root, generate)


def generate_change_text(node, parent, level):
    if is_compilation_unit(node):
        return generate_file_text(node, parent, level)
    elif is_class(node):
        return generate_class_text(node, parent, level)
    elif is_method(node):
        # return generate_method_text(node, parent, level)
    return None


def generate_file_text(node, parent, level):
    text = ""
    return text


def generate_class_text(node, parent, level):
    return "class_text"


def generate_method_text(node, parent, level):
    return "method_text"

    def visitor(node, parent, level):
        print("  " * level + node["uid"])


if __name__ == "__main__":
    # Do it for all files

    generate_change_text_for_file("workspace/Client_change_model.json")

    #
    # traverse_ast(before, visitor)
    # changes = compare_ast(before, after)
    # change_tree = build_change_tree(changes)
    # with open("workspace/Client_change_model.json", "w") as json_file:
    #     json.dump(change_tree, json_file, indent=4)
    # pass
