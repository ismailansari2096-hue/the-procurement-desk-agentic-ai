"""
Inspect workspace data, schemas, and competition files.
Generates/updates reports/workspace_inventory.md and reports/data_schema_report.md.
"""

import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from procurement.config import BASE_DIR, RAW_DATA_DIR, PLAYBOOK_DIR, REPORTS_DIR


def inspect_workspace():
    print("[*] Inspecting workspace files...")
    all_files = list(BASE_DIR.rglob("*"))
    file_list = [f for f in all_files if f.is_file() and ".git" not in f.parts and "__pycache__" not in f.parts]
    print(f"[+] Total workspace files tracked: {len(file_list)}")
    for f in sorted(file_list):
        rel = f.relative_to(BASE_DIR)
        print(f"  - {rel} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    inspect_workspace()
