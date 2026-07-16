import subprocess
from datetime import datetime

def create_branch():
    branch_name = datetime.now().strftime("%Y%m%d-%H%M%S")
    clean_branch_test = subprocess.run(["git","status","--porcelain"], capture_output=True, text=True)
    if clean_branch_test.stdout.strip() == "":
        switch_test = subprocess.run(["git","switch","-c", branch_name], capture_output=True, text=True)
        if switch_test.returncode == 0:
            return (True, branch_name)
        else:
            return (False, "Switch Fail")
    else:
        return (False, "Dirty Directory")