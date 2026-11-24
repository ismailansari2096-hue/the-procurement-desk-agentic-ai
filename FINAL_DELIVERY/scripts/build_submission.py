"""
Kaggle Submission Generator for The Procurement Desk.
Processes all 2,000 test threads from data/raw/threads.csv,
generates policy-compliant decisions, creates internal audit logs,
and exports and validates outputs/submission.csv.
"""

import sys
import csv
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from procurement.config import RAW_DATA_DIR, OUTPUTS_DIR, SUBMISSION_PATH, VALIDATION_REPORT_PATH, AUDIT_REPORT_PATH
from procurement.data_loader import load_threads
from procurement.decision_engine import DecisionEngine
from procurement.output_validator import OutputValidator


def build_submission():
    print("[*] Starting Kaggle Submission Generator...")
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    test_file = RAW_DATA_DIR / "threads.csv"
    if not test_file.exists():
        print(f"[-] Error: Test file not found at {test_file}")
        sys.exit(1)

    print(f"[*] Loading test threads from {test_file}...")
    threads = load_threads(test_file)
    print(f"[+] Loaded {len(threads)} test threads.")

    engine = DecisionEngine()
    validator = OutputValidator()

    predictions = []
    audit_trail = []

    print("[*] Processing threads through Deterministic Decision Engine...")
    for idx, thread in enumerate(threads, start=1):
        tid = thread["thread_id"]
        label, audit_info = engine.decide(thread)

        # Validate label immediately
        is_valid, msg, _ = validator.validate_label(label)
        if not is_valid:
            print(f"[-] FATAL: Invalid label generated for {tid}: {label} ({msg})")
            sys.exit(1)

        predictions.append((tid, label))
        audit_trail.append(audit_info)

        if idx % 500 == 0 or idx == len(threads):
            print(f"    Processed {idx}/{len(threads)} threads...")

    # Write submission CSV
    temp_submission = OUTPUTS_DIR / "submission_temp.csv"
    with open(temp_submission, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["thread_id", "label"])
        for tid, label in predictions:
            writer.writerow([tid, label])

    # Validate generated CSV independently
    print(f"[*] Running independent output validation on {temp_submission}...")
    validation_report = validator.validate_file(temp_submission, expected_rows=len(threads))

    with open(VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(validation_report, f, indent=2)

    if not validation_report["is_valid"]:
        print("[-] Submission validation FAILED! Details:")
        for err in validation_report["errors"][:10]:
            print(f"    Error: {err}")
        temp_submission.unlink(missing_ok=True)
        sys.exit(1)

    # Move valid temporary file to canonical SUBMISSION_PATH
    if SUBMISSION_PATH.exists():
        SUBMISSION_PATH.unlink()
    temp_submission.rename(SUBMISSION_PATH)

    # Save full audit trail
    with open(AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_trail, f, indent=2)

    print("=" * 60)
    print("[+] SUCCESS! Kaggle Submission generated and verified.")
    print(f"    Submission File  : {SUBMISSION_PATH} ({SUBMISSION_PATH.stat().st_size} bytes)")
    print(f"    Total Rows       : {validation_report['total_rows']}")
    print(f"    Action Breakdown : {validation_report['action_counts']}")
    print(f"    Validation Report: {VALIDATION_REPORT_PATH}")
    print(f"    Audit Trail      : {AUDIT_REPORT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    build_submission()
