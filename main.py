from monitor import test_code, parse_failure, extract_failure_details
from context import read_source_file, get_last_commit_message
from git_op import create_branch

def main():

    success, branch_name = create_branch()

    if not success:
        print(branch_name)
        return
    
    else:
        print(branch_name)
        res = test_code()

        if res.returncode == 0:
            print("All tests passed! No healing needed.")
            return

        print("Tests failed. Diagnosing...")
        failures = parse_failure(res.stdout)
        details = extract_failure_details(failures)
        commit_msg = get_last_commit_message()

        print("----------------------------")

        for failure in details:
            print(f"File: {failure['file']}, Test: {failure['test_name']}, Reason: {failure['reason']}")

            source = read_source_file(failure['file'])

            print("---source---")
            print(source)
            print("---last commit message---")
            print(commit_msg)
            print("----------------------------") 

if __name__ == "__main__":
    main()