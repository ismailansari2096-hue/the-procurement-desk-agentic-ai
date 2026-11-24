"""
Output Validator for Kaggle Submission.
Enforces strict competition rules:
1. thread_id,label columns only
2. Format: ACTION:REASON:COUNTER_PRICE
3. Trailing colons on non-COUNTER actions
4. Integer INR counter prices only on COUNTER
5. No missing, blank, or duplicate rows
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from procurement.config import VALID_ACTIONS, SUBMISSION_PATH, VALIDATION_REPORT_PATH


class OutputValidator:
    LABEL_PATTERN = re.compile(r"^([A-Z]+):([A-Z0-9_]+):(\d*)$")

    def __init__(self, allowed_reasons: set = None):
        self.allowed_reasons = allowed_reasons or set()

    def validate_label(self, label: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate a single label string."""
        if not label or not isinstance(label, str):
            return False, "Label is empty or not a string", {}

        match = self.LABEL_PATTERN.match(label.strip())
        if not match:
            return False, f"Label '{label}' does not match ACTION:REASON:COUNTER_PRICE format", {}

        action, reason, counter_price = match.groups()

        if action not in VALID_ACTIONS:
            return False, f"Invalid action '{action}'. Permitted: {sorted(list(VALID_ACTIONS))}", {}

        if self.allowed_reasons and reason not in self.allowed_reasons:
            return False, f"Reason '{reason}' not in allowed reasons for policy", {}

        if action == "COUNTER":
            if not counter_price:
                return False, "COUNTER action must have a non-empty counter price", {}
            try:
                price_val = int(counter_price)
                if price_val <= 0:
                    return False, f"Counter price must be positive, got {price_val}", {}
            except ValueError:
                return False, f"Counter price must be a valid integer, got '{counter_price}'", {}
        else:
            if counter_price:
                return False, f"Action '{action}' must have an empty counter price, got '{counter_price}'", {}

        parsed = {
            "action": action,
            "reason": reason,
            "counter_price": int(counter_price) if counter_price else None
        }
        return True, "Valid", parsed

    def validate_file(self, file_path: Path, expected_rows: int = None) -> Dict[str, Any]:
        """Validate the full submission CSV file."""
        report = {
            "is_valid": True,
            "total_rows": 0,
            "errors": [],
            "warnings": [],
            "action_counts": {},
            "duplicate_thread_ids": []
        }

        if not file_path.exists():
            report["is_valid"] = False
            report["errors"].append(f"File not found: {file_path}")
            return report

        seen_thread_ids = set()

        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                report["is_valid"] = False
                report["errors"].append("File is completely empty")
                return report

            if header != ["thread_id", "label"]:
                report["is_valid"] = False
                report["errors"].append(f"Invalid header: {header}. Expected ['thread_id', 'label']")

            for row_idx, row in enumerate(reader, start=2):
                if not row or (len(row) == 1 and not row[0].strip()):
                    report["is_valid"] = False
                    report["errors"].append(f"Line {row_idx}: Empty or blank row")
                    continue

                if len(row) != 2:
                    report["is_valid"] = False
                    report["errors"].append(f"Line {row_idx}: Row has {len(row)} columns, expected 2")
                    continue

                thread_id, label = row[0].strip(), row[1].strip()

                if not thread_id:
                    report["is_valid"] = False
                    report["errors"].append(f"Line {row_idx}: Missing thread_id")

                if thread_id in seen_thread_ids:
                    report["is_valid"] = False
                    report["duplicate_thread_ids"].append(thread_id)
                    report["errors"].append(f"Line {row_idx}: Duplicate thread_id '{thread_id}'")
                seen_thread_ids.add(thread_id)

                is_valid_lbl, msg, parsed = self.validate_label(label)
                if not is_valid_lbl:
                    report["is_valid"] = False
                    report["errors"].append(f"Line {row_idx} (thread {thread_id}): {msg}")
                else:
                    act = parsed["action"]
                    report["action_counts"][act] = report["action_counts"].get(act, 0) + 1

                report["total_rows"] += 1

        if expected_rows is not None and report["total_rows"] != expected_rows:
            report["is_valid"] = False
            report["errors"].append(f"Row count mismatch: found {report['total_rows']}, expected {expected_rows}")

        return report


def main():
    validator = OutputValidator()
    report = validator.validate_file(SUBMISSION_PATH)
    VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("Submission Validation Report:")
    print(json.dumps(report, indent=2))
    if not report["is_valid"]:
        exit(1)


if __name__ == "__main__":
    main()
