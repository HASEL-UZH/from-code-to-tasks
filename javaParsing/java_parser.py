import json
import os
from javalang.parser import Parser
from javalang.tokenizer import tokenize
from javalang.tree import CompilationUnit


def parse_java_to_ast(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    # Tokenize the code
    tokens = list(tokenize(code))

    # Initialize the parser with tokens
    parser = Parser(tokens)
    tree = parser.parse()
    print(type(tree))

    return tree

def save_ast_as_json(file_name, ast_dict, output_dir):
    output_path = os.path.join(output_dir, f'{file_name}.json')
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(ast_dict, json_file, indent=4)


def serialize_compilation_unit(compilation_unit):
    if not isinstance(compilation_unit, CompilationUnit):
        return None

    result = {
        'type': 'CompilationUnit',
        'package': compilation_unit.package.name if compilation_unit.package else None,
        'imports': [imp.path for imp in compilation_unit.imports],
        'types': []
    }

    for type_declaration in compilation_unit.types:
        type_dict = {
            'name': type_declaration.name,
            'type': type(type_declaration).__name__
            # Add more attributes based on your requirements
        }
        result['types'].append(type_dict)

    return result


def main():
    current_dir = os.getcwd()
    input_dir = os.path.join(current_dir, 'myJavaFileToParse.java')  # Replace with your Java file path
    output_dir = os.path.join(current_dir, 'astJson')  # Replace with your desired output directory

    os.makedirs(output_dir, exist_ok=True)

    # Parse Java code to AST and save as JSON

    ast = parse_java_to_ast(input_dir)
    print(ast)

    compilation_unit_dict = serialize_compilation_unit(ast)


    save_ast_as_json('myJavaTree', compilation_unit_dict, output_dir)

if __name__ == "__main__":
    main()
