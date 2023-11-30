from src.core.logger import log
from src.store.mdb_store import db


class JavaWriter:
    def __init__(self):
        self.line = ""
        self.content = []
        self._indent = 0

    def write(self, s):
        if not s:
            return
        self.line += s

    def write_ln(self, s):
        self.content.append(("    " * self._indent) + self.line + s)
        self.line = ""

    def indent(self):
        self._indent += 1

    def unindent(self):
        if self._indent >= 0:
            self._indent -= 1

    def package_def(self, package_name):
        self.write_ln(f"package {package_name};")

    def import_def(self, import_name):
        self.write_ln(f"import {import_name};")

    def class_def(self, class_name):
        self.write_ln(f"public class {class_name} {{")
        self.indent()

    def method_def(self, method_name):
        self.write_ln(f"public void {method_name}() {{")
        self.indent()

    def identifier_def(self, identifier_name):
        self.write_ln(f"var {identifier_name} = 0;")

    def end_statement(self):
        self.unindent()
        self.write_ln("}")

    def line_comment(self, comment):
        self.write_ln(f"// {comment}")

    def multiline_comment(self, comment):
        self.write_ln("/*")
        lines = lines = comment.split("\n")

        for line in lines:
            self.write_ln(line)
        self.write_ln("*/")

    def get_code(self):
        return "\n".join(self.content)


def create_meta_ast_code(resource):
    resource_content = db.get_resource_content(resource)
    java = JavaWriter()
    for i, cu_node in enumerate(resource_content["code"]["details"]):
        if not cu_node:
            log.error(
                f"No code.details in resource {resource_content.get('filename')} at index {i}"
            )
            continue
        cu_change = cu_node.get("change", {})
        cu = cu_change.get("after")
        if not cu:
            return None

        def get_after(node):
            return node.get("change", {}).get("after") or None

        def write_comments(parent):
            comments = [
                obj
                for obj in parent.get("children", [])
                if obj.get("type") == "comment" and obj.get("change", {}).get("after")
            ]
            for comment in comments:
                _comment = get_after(comment)
                if "license" in _comment["content"]:
                    continue
                multiline = "\n" in _comment["content"]
                if multiline:
                    java.multiline_comment(_comment["content"])
                else:
                    java.line_comment(_comment["content"])
            pass

        write_comments(cu_node)
        java.package_def(cu["package"])
        imports = [
            obj
            for obj in cu_node["children"]
            if obj.get("type") == "import" and obj.get("change", {}).get("after")
        ]
        classes = [
            obj
            for obj in cu_node["children"]
            if obj.get("type") == "class" and obj.get("change", {}).get("after")
        ]

        for imp in imports:
            _imp = get_after(imp)
            if _imp:
                java.import_def(_imp["identifier"])

        for cl in classes:
            _cl = get_after(cl)
            if _cl:
                java.class_def(_cl["identifier"])
                write_comments(_cl)
                methods = [
                    obj
                    for obj in cl["children"]
                    if obj.get("type") == "method"
                    and obj.get("change", {}).get("after")
                ]
                for method in methods:
                    _method = get_after(method)
                    if _method:
                        java.method_def(_method["identifier"])
                        write_comments(_method)
                        identifiers = [
                            obj
                            for obj in method["children"]
                            if obj.get("type") == "identifier"
                            and obj.get("change", {}).get("after")
                        ]
                        for identifier in identifiers:
                            _identifier = get_after(identifier)
                            if _identifier:
                                java.identifier_def(_identifier["identifier"])
                                write_comments(_identifier)
                        java.end_statement()
                java.end_statement()

    code = java.get_code()
    return code
