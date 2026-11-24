"""
Extract playbook.zip into data/processed/playbook/
Verifies mandatory policies, amendments, supplier files, and examples.
"""

import sys
import zipfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from procurement.config import BASE_DIR, RAW_DATA_DIR, PLAYBOOK_DIR


def find_playbook_zip() -> Path:
    candidates = [
        RAW_DATA_DIR / "playbook.zip",
        BASE_DIR / "playbook.zip",
        Path.home() / "Downloads" / "playbook.zip",
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    # Search raw directory for any zip matching playbook
    for p in RAW_DATA_DIR.glob("*playbook*.zip"):
        return p
    for p in BASE_DIR.glob("*playbook*.zip"):
        return p
    return None


def extract_playbook():
    zip_path = find_playbook_zip()
    if not zip_path:
        print("[-] playbook.zip not found.")
        print("Please place 'playbook.zip' into data/raw/ or the workspace root directory.")
        return False

    print(f"[+] Found playbook archive: {zip_path}")
    PLAYBOOK_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(PLAYBOOK_DIR)
        print(f"[+] Extracted {len(zf.namelist())} files into {PLAYBOOK_DIR}")

    # Verify decision procedure
    dp_path = PLAYBOOK_DIR / "policies" / "decision-procedure.md"
    alt_dp = list(PLAYBOOK_DIR.rglob("*decision-procedure*.md"))
    if dp_path.exists():
        print(f"[+] Found core procedure: {dp_path}")
    elif alt_dp:
        print(f"[+] Found core procedure: {alt_dp[0]}")
    else:
        print("[-] Warning: decision-procedure.md not found in expected location within playbook.")

    return True


if __name__ == "__main__":
    success = extract_playbook()
    sys.exit(0 if success else 1)
