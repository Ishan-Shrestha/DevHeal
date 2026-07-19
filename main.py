from monitor import test_code, parse_failure, extract_failure_details
from context import read_source_file, get_last_commit_message
from git_op import create_branch
from healer import build_prompt, call_llm, apply_patch

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
            file_path = failure['file']

            prompt = build_prompt(failure, source, commit_msg)
            corrected_code = call_llm(prompt)
            apply_patch(file_path, corrected_code)
        verification = test_code()
        if verification.returncode == 0:
            print("All tests passed! No additional healing needed.")
        else:
            print("Some tests still failing after patch attempts.")
if __name__ == "__main__":
    main()