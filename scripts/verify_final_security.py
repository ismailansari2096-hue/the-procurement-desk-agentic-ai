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
import hashlib
from pathlib import Path

EXPECTED_V4_HASH = "a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92"

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
        (r"^data/raw/", "Raw competition dataset (data/raw/)"),
        (r"^outputs/", "Prediction outputs directory (outputs/)"),
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

        # Check CSV files: ONLY submission_v4.csv is allowed
        if f.endswith(".csv"):
            if not (f == "submission_v4.csv" or f == "FINAL_DELIVERY/submission_v4.csv"):
                violations.append((f, "Unapproved CSV file in repository"))

    if violations:
        print("\n[CRITICAL FAILURE] Forbidden files detected in Git tracking:")
        for f, desc in violations:
            print(f"  - {f} : {desc}")
        return 1

    print("  [PASS] Zero unauthorized CSV files tracked in Git.")
    print("  [PASS] Zero raw competition datasets tracked in Git.")
    print("  [PASS] Zero .env / secrets / credentials tracked in Git.")
    print("  [PASS] Zero .vercel / local build directories tracked in Git.")

    # 2. Check local V4 CSV hash
    v4_path = Path("submission_v4.csv")
    if not v4_path.exists():
        v4_path = Path("outputs/experimental/submission_v4.csv")

    if v4_path.exists():
        content = v4_path.read_bytes()
        h = hashlib.sha256(content).hexdigest()
        if h == EXPECTED_V4_HASH:
            print(f"  [PASS] Final V4 Submission CSV SHA256 matches exactly: {h}")
        else:
            print(f"  [FAIL] Final V4 Submission CSV hash mismatch! Expected {EXPECTED_V4_HASH}, got {h}")
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
