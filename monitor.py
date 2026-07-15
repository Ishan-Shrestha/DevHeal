import subprocess

# TESTING BRANCHES
def test_code():
    """Runs pytest and returns the subprocess result."""
    res = subprocess.run(['pytest'], capture_output=True, text=True)
    return res

def parse_failure(stdout):
    """Parses the test results into individual parts and return the failures compiled as a list."""
    failed_cases = []
    for line in stdout.splitlines():
        if line.startswith('FAILED'):
            failed_cases.append(line)
    return failed_cases
    
def extract_failure_details(failures):
    """Extracts the details such as 'file-name', 'test-name' and 'reason' from the failure cases."""
    failure_detail = []
    for fail_case in failures:
        failure_dict = {}
        file_name = fail_case.split('FAILED')[1].split('::')[0].strip()
        test_error = fail_case.split('FAILED')[1].split('::')[1].split(' - ', 1)
        failure_dict["file"] = file_name
        failure_dict["test_name"] = test_error[0].strip()
        failure_dict["reason"] = test_error[1].strip()
        failure_detail.append(failure_dict)
    return failure_detail
