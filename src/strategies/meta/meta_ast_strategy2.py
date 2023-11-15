from typing import Protocol, Any

from src.ast.meta_ast_object_factory import (
    get_compilation_unit_obj,
    get_import_obj,
    get_package_obj,
    get_class_obj,
    get_method_obj,
    get_identifier_obj,
    get_comment_obj,
)

COMPILATION_UNIT = "com.github.javaparser.ast.CompilationUnit"
PACKAGE = "com.github.javaparser.ast.PackageDeclaration"
IMPORT = "com.github.javaparser.ast.ImportDeclaration"
CLASS = "com.github.javaparser.ast.body.ClassOrInterfaceDeclaration"
METHOD = "com.github.javaparser.ast.body.MethodDeclaration"
IDENTIFIER = "com.github.javaparser.ast.body.VariableDeclarator"
COMMENT_LINE = "com.github.javaparser.ast.comments.LineComment"
COMMENT_BLOCK = "com.github.javaparser.ast.comments.BlockComment"
COMMENT_JAVADOC = "com.github.javaparser.ast.comments.JavadocComment"

CONTAINER_CLASSES = [COMPILATION_UNIT, PACKAGE, CLASS, METHOD, IDENTIFIER]


class IVisitor(Protocol):
    def visit_before(self, value: Any, key: Any, parent: Any, level: int) -> None:
        ...

    def visit_after(self, value: Any, key: Any, parent: Any, level: int) -> None:
        ...


class MetaAstBuilder(IVisitor):
    def __init__(self, filename, opts=None):
        self.root = None
        self.stack = []
        self.filename = filename
        self.options = MetaAstBuilder.get_options(opts)

    @staticmethod
    def get_options(opts):
        default_opts = {
            "imports": True,
            "methods": True,
            "identifiers": True,
            "comments": True,
        }
        options = {**default_opts, **(opts or {})}
        return options

    def peek(self):
        return self.stack[-1]

    def pop(self):
        return self.stack.pop()

    def push(self, obj):
        if not self.stack:
            if not self.root:
                self.root = obj
            else:
                raise Exception("Invalid stack (multiple roots)")

        self.stack.append(obj)
        return obj

    def isEmpty(self):
        return not self.stack

    def is_container(self, obj_class: str):
        return obj_class in CONTAINER_CLASSES

    def is_interface(self, node, obj_class):
        return obj_class == CLASS and node.get("isInterface") == "true"

    def get_comment_type(self, obj_class):
        comments = {
            COMMENT_LINE: "line",
            COMMENT_BLOCK: "block",
            COMMENT_JAVADOC: "javadoc",
        }
        return comments.get(obj_class)

    def add_import(self, container, imp):
        if imp:
            if "imports" not in container:
                container["imports"] = []
            container["imports"].append(imp)

    def add_comment(self, container, comment):
        if comment:
            if "comments" not in container:
                container["comments"] = []
            container["comments"].append(comment)

    def is_comment(self, obj_class):
        return self.get_comment_type(obj_class) != None

    def get_root(self):
        return self.root

    def visit_before(self, value: Any, key: Any, parent: Any, level: int) -> None:
        if isinstance(value, dict):
            if "!" in value:
                obj_class = value["!"]

                if obj_class == COMPILATION_UNIT:
                    if not self.isEmpty():
                        raise Exception("Invalid stack (compilation unit)")
                    obj = get_compilation_unit_obj(self.filename)
                    self.push(obj)

                elif obj_class == IMPORT:
                    if self.options.get("imports"):
                        container = self.peek()
                        obj = get_import_obj(container["uid"], value)
                        self.add_import(container, obj)
                    return False

                elif obj_class == PACKAGE:
                    container = self.peek()
                    obj = get_package_obj(container["uid"], value)
                    container["children"].append(obj)
                    self.push(obj)

                elif obj_class == CLASS:
                    if self.is_interface(value, obj_class):
                        return False
                    container = self.peek()
                    obj = get_class_obj(container["uid"], value)
                    container["children"].append(obj)
                    self.push(obj)

                elif obj_class == METHOD:
                    if self.options.get("methods"):
                        container = self.peek()
                        obj = get_method_obj(container["uid"], value)
                        container["children"].append(obj)
                        self.push(obj)
                    else:
                        return False

                elif obj_class == IDENTIFIER:
                    if self.options.get("identifiers"):
                        container = self.peek()
                        obj = get_identifier_obj(container["uid"], value)
                        container["children"].append(obj)
                        self.push(obj)
                    else:
                        return False

                elif self.is_comment(obj_class):
                    if self.options.get("comments"):
                        container = self.peek()
                        obj = get_comment_obj(container["uid"], parent)
                        self.add_comment(container, obj)
                    return False

    def visit_after(self, value: Any, key: Any, parent: Any, level: int) -> None:
        if isinstance(value, dict):
            if "!" in value:
                obj_class = value["!"]
                if self.is_container(obj_class):
                    self.pop()
        pass


def traverse_json_structure(
    json_structure: Any,
    visitor: IVisitor,
    key: Any = None,
    parent: Any = None,
    level: int = 0,
) -> None:
    """
    Traverse a JSON structure, calling visitor methods before and after visiting each node.

    :param json_structure: The JSON structure to traverse.
    :param visitor: An instance of a class that implements the IVisitor protocol.
    :param key: The current key in the parent object, or None if root.
    :param parent: The parent object, or None if root.
    :param level: The current depth level in the JSON structure.
    """
    check = visitor.visit_before(json_structure, key, parent, level)

    if check != False:
        if isinstance(json_structure, dict):
            for k, v in json_structure.items():
                traverse_json_structure(
                    v, visitor, key=k, parent=json_structure, level=level + 1
                )
        elif isinstance(json_structure, list):
            for idx, item in enumerate(json_structure):
                traverse_json_structure(
                    item, visitor, key=idx, parent=json_structure, level=level + 1
                )

        visitor.visit_after(json_structure, key, parent, level)
