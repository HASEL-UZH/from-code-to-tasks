import subprocess

def traverse_files():
    pass

def create_java_ast_(in_file, out_file):
    command = ['java', '-jar', './AstMetaWorkSpace/ast-meta-werks-0.1.1.jar', in_file, out_file]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode!=0:
        raise Exception("Error running the Java class.")

    return result.stdout.strip()

if __name__=="__main__":
    create_java_ast_('AstMetaWorkspace/data/in/Example.java', 'AstMetaWorkspace/data/out/Example2.ast.json' )