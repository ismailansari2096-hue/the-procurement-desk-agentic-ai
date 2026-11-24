import pytest
import csv
from pathlib import Path
from procurement.output_validator import OutputValidator


def test_valid_labels():
    validator = OutputValidator()
    
    # Accept format
    ok, msg, p = validator.validate_label("ACCEPT:ACCEPTABLE_PRICE:")
    assert ok, msg
    assert p["action"] == "ACCEPT"
    assert p["reason"] == "ACCEPTABLE_PRICE"
    assert p["counter_price"] is None

    # Counter format with integer price
    ok, msg, p = validator.validate_label("COUNTER:COUNTER_OFFER:21500")
    assert ok, msg
    assert p["action"] == "COUNTER"
    assert p["reason"] == "COUNTER_OFFER"
    assert p["counter_price"] == 21500

    # Reject format
    ok, msg, p = validator.validate_label("REJECT:ABOVE_WALKAWAY:")
    assert ok, msg
    assert p["action"] == "REJECT"
    assert p["reason"] == "ABOVE_WALKAWAY"
    assert p["counter_price"] is None

    # Escalate format
    ok, msg, p = validator.validate_label("ESCALATE:PROMPT_INJECTION:")
    assert ok, msg
    assert p["action"] == "ESCALATE"
    assert p["reason"] == "PROMPT_INJECTION"
    assert p["counter_price"] is None


def test_invalid_labels():
    validator = OutputValidator()

    # Missing trailing colon on non-counter
    ok, msg, _ = validator.validate_label("ACCEPT:ACCEPTABLE_PRICE")
    assert not ok

    # Price on non-counter
    ok, msg, _ = validator.validate_label("ACCEPT:ACCEPTABLE_PRICE:1000")
    assert not ok

    # Missing price on counter
    ok, msg, _ = validator.validate_label("COUNTER:COUNTER_OFFER:")
    assert not ok

    # Float price
    ok, msg, _ = validator.validate_label("COUNTER:COUNTER_OFFER:21500.50")
    assert not ok

    # Price with comma / currency
    ok, msg, _ = validator.validate_label("COUNTER:COUNTER_OFFER:INR21500")
    assert not ok
    ok, msg, _ = validator.validate_label("COUNTER:COUNTER_OFFER:21,500")
    assert not ok

    # Unknown action
    ok, msg, _ = validator.validate_label("HOLD:WAIT_SUPPLIER:")
    assert not ok


def test_csv_validation(tmp_path):
    validator = OutputValidator()
    csv_file = tmp_path / "test_sub.csv"
    
    # Valid CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["thread_id", "label"])
        writer.writerow(["T1001", "ACCEPT:ACCEPTABLE_PRICE:"])
        writer.writerow(["T1002", "COUNTER:COUNTER_OFFER:21500"])
        writer.writerow(["T1003", "REJECT:ABOVE_WALKAWAY:"])
        writer.writerow(["T1004", "ESCALATE:PROMPT_INJECTION:"])

    report = validator.validate_file(csv_file, expected_rows=4)
    assert report["is_valid"]
    assert report["total_rows"] == 4
    assert report["action_counts"]["ACCEPT"] == 1
    assert report["action_counts"]["COUNTER"] == 1
    assert report["action_counts"]["REJECT"] == 1
    assert report["action_counts"]["ESCALATE"] == 1

    # Duplicate thread_id failure
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["thread_id", "label"])
        writer.writerow(["T1001", "ACCEPT:ACCEPTABLE_PRICE:"])
        writer.writerow(["T1001", "COUNTER:COUNTER_OFFER:21500"])

    report = validator.validate_file(csv_file)
    assert not report["is_valid"]
    assert "T1001" in report["duplicate_thread_ids"]
