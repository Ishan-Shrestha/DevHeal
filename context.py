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