"""
Comprehensive Competition QA and Integrity Verifier.
Checks row counts, formatting, missing values, duplicates, ID matching,
and cryptographic/byte-level preservation of submission files.
"""

import csv
import re
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_THREADS = BASE_DIR / "data" / "raw" / "threads.csv"
V1_PATH = BASE_DIR / "outputs" / "submission.csv"
V1_BACKUP = BASE_DIR / "outputs" / "backup" / "submission_v1.csv"
V2_PATH = BASE_DIR / "outputs" / "experimental" / "submission_v2.csv"

LABEL_PATTERN = re.compile(r"^(ACCEPT|COUNTER|REJECT|ESCALATE):([A-Z_]+):(\d+)?$")
VALID_ACTIONS = {"ACCEPT", "COUNTER", "REJECT", "ESCALATE"}
VALID_REASONS = {
    "ACCEPTABLE_PRICE",
    "COUNTER_OFFER",
    "ABOVE_WALKAWAY",
    "BLACKLISTED_SUPPLIER",
    "BANNED_TERM",
    "PROMPT_INJECTION",
    "MISSING_INFO",
    "OVER_APPROVAL_LIMIT"
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def validate_submission_file(path: Path, expected_ids: list):
    assert path.exists(), f"File missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 2000, f"Expected 2000 rows, got {len(reader)}"
    assert reader[0].keys() == {"thread_id", "label"}, f"Invalid headers: {reader[0].keys()}"

    seen_ids = set()
    for idx, row in enumerate(reader):
        tid = row["thread_id"]
        label = row["label"]

        assert tid, f"Empty thread_id at row {idx}"
        assert label, f"Empty label at row {idx}"
        assert tid == expected_ids[idx], f"Thread ID mismatch at row {idx}: {tid} != {expected_ids[idx]}"
        assert tid not in seen_ids, f"Duplicate thread_id: {tid}"
        seen_ids.add(tid)

        m = LABEL_PATTERN.match(label)
        assert m, f"Label does not match competition format at row {idx}: '{label}'"

        action, reason, counter = m.group(1), m.group(2), m.group(3) or ""
        assert action in VALID_ACTIONS, f"Invalid action: {action}"
        assert reason in VALID_REASONS, f"Invalid reason: {reason}"

        if action == "COUNTER":
            assert reason == "COUNTER_OFFER", f"Counter action must have reason COUNTER_OFFER, got {reason}"
            assert counter != "", f"Counter action missing price at row {idx}"
            assert counter.isdigit(), f"Counter price must be integer, got {counter}"
        else:
            assert counter == "", f"Non-counter action {action} has counter price '{counter}' at row {idx}"

    return len(reader)


def main():
    print("=" * 70)
    print("  COMPREHENSIVE COMPETITION INTEGRITY & QA AUDIT")
    print("=" * 70)

    # 1. Load ground truth thread IDs
    with open(RAW_THREADS, "r", encoding="utf-8") as f:
        raw_ids = [r["thread_id"] for r in csv.DictReader(f)]
    print(f"[✓] Loaded {len(raw_ids)} raw test thread IDs.")

    # 2. Check V1 baseline
    v1_count = validate_submission_file(V1_PATH, raw_ids)
    v1_hash = compute_sha256(V1_PATH)
    print(f"[✓] Submission V1 ({V1_PATH.name}): {v1_count} rows passed all checks.")
    print(f"    SHA-256: {v1_hash}")

    # 3. Check V1 backup
    v1_b_count = validate_submission_file(V1_BACKUP, raw_ids)
    v1_b_hash = compute_sha256(V1_BACKUP)
    assert v1_hash == v1_b_hash, "Backup V1 hash does not match submission V1!"
    print(f"[✓] Backup V1 ({V1_BACKUP.name}): Perfect byte-for-byte match to V1.")

    # 4. Check V2 experimental
    v2_count = validate_submission_file(V2_PATH, raw_ids)
    v2_hash = compute_sha256(V2_PATH)
    print(f"[✓] Submission V2 ({V2_PATH.name}): {v2_count} rows passed all checks.")
    print(f"    SHA-256: {v2_hash}")

    # 5. Measure exact delta between V1 and V2
    with open(V1_PATH, "r", encoding="utf-8") as f1, open(V2_PATH, "r", encoding="utf-8") as f2:
        r1 = list(csv.DictReader(f1))
        r2 = list(csv.DictReader(f2))

    diff_count = sum(1 for a, b in zip(r1, r2) if a["label"] != b["label"])
    print(f"[✓] Exact prediction delta between V1 and V2: {diff_count} rows (6.60% of test set).")
    assert diff_count == 132, f"Expected 132 changed predictions, got {diff_count}"

    print("\n" + "=" * 70)
    print("  ALL COMPETITION DATA INTEGRITY AUDITS PASSED CLEANLY (100%)")
    print("=" * 70)


if __name__ == "__main__":
    main()
