from monitor import test_code, parse_failure, extract_failure_details
from context import read_source_file, get_last_commit_message, get_tested_modules
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

        print("----------------------------")
        for failure in details:
            print(f"File: {failure['file']}, Test: {failure['test_name']}, Reason: {failure['reason']}")
            test_filepath = failure['file']
            test_source = read_source_file(test_filepath)
            commit_msg = get_last_commit_message(test_filepath)

            # Don't just look at the test file - pull in the source module(s) it
            # actually imports and tests, so the LLM can see whether the bug lives
            # in the implementation instead of always rewriting the test.
            tested_module_paths = get_tested_modules(test_filepath)
            related_sources = {
                path: read_source_file(path) for path in tested_module_paths
            }

            prompt = build_prompt(failure, test_filepath, test_source, related_sources, commit_msg)
            result = call_llm(prompt)

            if result is None:
                print(f"Healer failed to produce a fix for {test_filepath}, skipping.")
                continue

            target_file = result['file']
            corrected_code = result['code']
            print(f"Healer chose to patch: {target_file}")
            apply_patch(target_file, corrected_code)

        verification = test_code()
        if verification.returncode == 0:
            print("All tests passed! No additional healing needed.")
        else:
            print("Some tests still failing after patch attempts.")
if __name__ == "__main__":
    main()
