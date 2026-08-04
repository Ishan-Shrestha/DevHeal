import ast
import os
import subprocess

def read_source_file(filepath):
    """Reads and returns the content of the given source file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        return None
    
def get_last_commit_message(filename):
    """Returns the last git commit message that touched the given file."""
    res = subprocess.run(['git', 'log', '-1', '--pretty=%B', '--', filename], capture_output=True, text=True)
    return res.stdout.strip()

def get_tested_modules(test_filepath):
    """
    Parses a test file's imports and returns the paths of any local modules it
    imports from (i.e. the actual code under test), so the healer can see the
    implementation, not just the test.
    """
    source = read_source_file(test_filepath)
    if not source:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    base_dir = os.path.dirname(test_filepath) or '.'
    module_paths = set()

    for node in ast.walk(tree):
        module_names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            module_names.append(node.module)
        elif isinstance(node, ast.Import):
            module_names.extend(alias.name for alias in node.names)

        for name in module_names:
            candidate = os.path.join(base_dir, name.replace('.', os.sep) + '.py')
            if os.path.isfile(candidate):
                module_paths.add(os.path.normpath(candidate))

    return sorted(module_paths)