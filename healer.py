from dotenv import load_dotenv
import json
import os
import re
import requests
from context import read_source_file

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
url = "https://generativelanguage.googleapis.com/v1beta/interactions"

headers = {
    "x-goog-api-key": key,
    "Content-Type": "application/json"
}

BASE_PROMPT = (
    "You are an automated code-fixing tool. You will be given a failing test file, "
    "the source module(s) that test file imports and exercises, the failure details "
    "pytest reported, and the commit message that most recently touched the test file "
    "(as a signal of intent). A failing test does not mean the test itself is wrong: "
    "the bug may be in the test's expectations, OR in the implementation of the source "
    "module it is testing. Compare the test's expected/intended behavior against what "
    "each source module actually does, and decide which single file truly contains the "
    "mistake. Prefer fixing the source module's implementation over changing a test's "
    "expected value, unless the test itself is clearly asserting the wrong thing. "
    "Then return ONLY that one corrected file, in full. "
    "Respond with strict JSON and nothing else - no markdown fences, no explanation, "
    "no extra keys: "
    "{\"file\": \"<the exact path of the one file you are fixing, matching one of the "
    "paths given below>\", \"code\": \"<the complete corrected content of that file>\"}\n"
    "The issue with the code is:\n"
)

def build_prompt(failure, test_filepath, test_source, related_sources, commit_message):
    """
    Builds a prompt from the failure case, the failing test file, the source module(s)
    it tests, and the last commit message, so the model can judge which file is actually
    wrong instead of always rewriting the test.
    """
    prompt = BASE_PROMPT
    for key, value in failure.items():
        prompt += f"\n{key}: {value}"

    prompt += f"\n\ntest_file: {test_filepath}\ntest_source:\n{test_source}"

    for path, content in related_sources.items():
        prompt += f"\n\nsource_file: {path}\nsource_code:\n{content}"

    prompt += f"\n\nintent (last commit message touching the test file): {commit_message}"
    return prompt

def call_llm(prompt):
    """Takes a correction prompt and returns a dict: {'file': <path>, 'code': <corrected code>}"""
    payload = {
        "model": "gemini-3.1-flash-lite",
        "input": prompt
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        response_data = response.json()
        steps = response_data.get("steps", [])

        output = None
        for step in steps:
            if step['type'] == 'model_output':
                output = step['content'][0]['text']
                break

        if output is None:
            print("No model_output step found in response")
            return None

        # Defensively strip markdown fences in case the model adds them anyway
        cleaned = re.sub(r'^```(?:json)?|```$', '', output.strip(), flags=re.MULTILINE).strip()
        result = json.loads(cleaned)

        if 'file' not in result or 'code' not in result:
            print(f"Malformed healer response, missing 'file' or 'code': {result}")
            return None

        return result

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
        print(f"Response Body: {response.text}")
        return None
    except json.JSONDecodeError as json_err:
        print(f"Failed to parse healer response as JSON: {json_err}")
        return None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None

def apply_patch(filepath, newcode):
    """Takes the path of the file to fix, creates a backup file and overrides the original file with corrected code"""
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
