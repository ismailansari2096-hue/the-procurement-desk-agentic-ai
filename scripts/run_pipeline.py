"""
Master Pipeline Runner for The Procurement Desk.
Orchestrates:
1. Workspace inspection & playbook extraction
2. Automated regression tests (pytest)
3. Worked-example evaluation
4. Kaggle submission generation
5. Output validation
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def run_step(step_name: str, command: list):
    print(f"\n>>> [PIPELINE STEP] {step_name}")
    res = subprocess.run(command, cwd=str(BASE_DIR))
    if res.returncode != 0:
        print(f"[-] Step '{step_name}' failed with return code {res.returncode}")
        sys.exit(res.returncode)
    print(f"[+] Step '{step_name}' completed successfully.")


def main():
    print("=" * 70)
    print("THE PROCUREMENT DESK — END-TO-END PIPELINE")
    print("=" * 70)

    run_step("1. Inspect Data & Workspace", [sys.executable, "scripts/inspect_data.py"])
    run_step("2. Run Automated Test Suite", [sys.executable, "-m", "pytest", "-v"])
    run_step("3. Evaluate Worked Examples", [sys.executable, "scripts/evaluate_examples.py"])
    run_step("4. Build Kaggle Submission", [sys.executable, "scripts/build_submission.py"])
    run_step("5. Validate Final Submission", [sys.executable, "scripts/validate_submission.py"])

    print("\n" + "=" * 70)
    print("[+] FULL PIPELINE EXECUTED SUCCESSFULLY — ALL QUALITY GATES PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
