import subprocess
import sys

def run_test(inputs):
    print(f"--- Running with inputs: {inputs} ---")
    input_str = "\n".join(inputs) + "\n"
    process = subprocess.Popen(
        [sys.executable, "semantics/semantics1.py", "reproduce_issue.lol"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=r"c:\Users\Djeana Carel Briones\OneDrive\Documents\124\cmsc-124-project"
    )
    stdout, stderr = process.communicate(input=input_str)
    print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)

run_test(["1", "2000"])
run_test(["2", "100"])
run_test(["3", "5"])
run_test(["0"])
