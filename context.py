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

def get_last_commit_message():
    """Returns the last git commit message."""
    res = subprocess.run(['git', 'log', '-3', '--pretty=%B'], capture_output=True, text=True)
    return res.stdout.strip()