from dotenv import load_dotenv
import os
import requests
from context import read_source_file

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
url = "https://generativelanguage.googleapis.com/v1beta/interactions"

headers = {
    "x-goog-api-key": key,
    "Content-Type": "application/json"
}

BASE_PROMPT = 'You are an automated code-fixing tool. You do not explain, apologize, or add any metadata feedack except the corrected code itself. Return the complete corrected version of this file. Do not include markdown code fences, explanations, or any text other than the raw code. The issue with the code are:\n'

def build_prompt(failure, source, commit_message):
    prompt = BASE_PROMPT
    for key, value in failure.items():
        prompt += f"\n{key}: {value}"

    prompt += '\ncodesource: ' + source + '\nintent: ' + commit_message
    return prompt

def call_llm(prompt):
    payload = {
        "model": "gemini-3.1-flash-lite",
        "input": prompt
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        response_data = response.json()
        steps = response_data.get("steps", [])

        for step in steps:
            if step['type'] == 'model_output':
                output = step['content'][0]['text']
                break

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
        print(f"Response Body: {response.text}")
        return None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None
    
    return output

def apply_patch(filepath, newcode):
    try:
        file = read_source_file(filepath)
        backup_path = filepath + ".bak" 
        with open(backup_path, 'w') as f:
            f.write(file)
        with open(filepath, 'w') as f:
            f.write(newcode)
        return True
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        return None


if __name__ == "__main__":
    test_failure = {"file": "test_dummy.py", "test_name": "test_fail", "reason": "assert 1 == 2"}
    test_source = "def test_fail():\n    assert 1==2\n"
    prompt = build_prompt(test_failure, test_source, "test: trivial change on test-branch")
    result = call_llm(prompt)
    print(result)