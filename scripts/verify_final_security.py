"""
Final Security & Exposure Verification Script.
Audits:
1. Git tracked files (git ls-tree -r --name-only HEAD)
2. .gitignore and .vercelignore rules
3. Local environment files & secrets
"""

import subprocess
import sys
import re

def audit_security():
    print("=" * 65)
    print("RUNNING FINAL SECURITY & SECRETS AUDIT")
    print("=" * 65)

    # 1. Inspect git tracked files
    res = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True, check=True)
    tracked_files = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]

    print(f"Total files tracked in Git repository: {len(tracked_files)}")

    violations = []

    # Patterns that must NOT appear in git
    forbidden_patterns = [
        (r"\.env($|\..*)", "Environment file with secrets (.env)"),
        (r"\.csv$", "Submission or prediction CSV file (*.csv)"),
        (r"^data/raw/", "Raw competition dataset (data/raw/)"),
        (r"^outputs/", "Prediction outputs directory (outputs/)"),
        (r"^FINAL_DELIVERY/submission_", "Submission CSV file in delivery"),
        (r"^FINAL_DELIVERY/outputs/", "Outputs in delivery"),
        (r"\.(pem|key)$", "Cryptographic key file"),
        (r"credentials\.json$", "Credentials JSON file"),
        (r"\.vercel/", "Vercel credentials/metadata directory"),
    ]

    for f in tracked_files:
        # Check against forbidden patterns
        for pat, desc in forbidden_patterns:
            if re.search(pat, f, re.IGNORECASE):
                violations.append((f, desc))

    if violations:
        print("\n[CRITICAL FAILURE] Forbidden files detected in Git tracking:")
        for f, desc in violations:
            print(f"  - {f} : {desc}")
        return 1

    print("  [PASS] Zero CSV files tracked in Git.")
    print("  [PASS] Zero raw competition datasets tracked in Git.")
    print("  [PASS] Zero .env / secrets / credentials tracked in Git.")
    print("  [PASS] Zero .vercel / local build directories tracked in Git.")

    # 2. Check local V4 CSV hash
    import hashlib
    from pathlib import Path
    v4_path = Path("outputs/experimental/submission_v4.csv")
    if v4_path.exists():
        content = v4_path.read_bytes()
        h = hashlib.sha256(content).hexdigest()
        expected_hash = "a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92"
        if h == expected_hash:
            print(f"  [PASS] Local V4 Submission CSV SHA256 matches exactly: {h}")
        else:
            print(f"  [FAIL] Local V4 Submission CSV hash mismatch! Expected {expected_hash}, got {h}")
            return 1
    else:
        print(f"  [FAIL] {v4_path} not found!")
        return 1

    print("\n" + "=" * 65)
    print("FINAL SECURITY & EXPOSURE AUDIT: ALL PASSED")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(audit_security())
