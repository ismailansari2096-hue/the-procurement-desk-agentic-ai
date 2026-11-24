"""
Audit git staging to verify that all datasets, CSVs, and secrets are excluded.
"""

import subprocess
import sys

def main():
    print("=" * 65)
    print("AUDITING GIT STAGING & .GITIGNORE RULES")
    print("=" * 65)

    dry = subprocess.run(["git", "add", "--dry-run", "."], capture_output=True, text=True)
    added_files = [l.split("add ")[-1].strip("'\" ") for l in dry.stdout.splitlines() if "add " in l]
    print(f"Total files that would be tracked: {len(added_files)}")

    forbidden = [
        f for f in added_files 
        if f.endswith((".csv", ".zip", ".tar", ".gz", ".env"))
        or "secret" in f.lower() 
        or "credential" in f.lower() 
        or "temp_chrome" in f.lower() 
        or "data/raw" in f.replace("\\", "/")
        or "raw" in f.lower()
        or "outputs" in f.replace("\\", "/")
    ]

    print(f"Forbidden files detected: {len(forbidden)}")
    if forbidden:
        print("ALERT! Forbidden files detected:")
        for fb in forbidden:
            print(f"  [FORBIDDEN] {fb}")
        sys.exit(1)
    else:
        print("[VERIFIED] Zero CSV files, Zero ZIP archives, Zero secrets, Zero raw datasets!")

    print("\nSample of files that ARE safe and included for deployment:")
    for f in added_files[:15]:
        print(f"  [SAFE] {f}")

    print("=" * 65)
    print("GIT AUDIT PASSED: SAFE FOR REPO CREATION")

if __name__ == "__main__":
    main()
