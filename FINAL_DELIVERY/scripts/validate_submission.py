"""
Validation script for Kaggle submission CSV.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from procurement.config import SUBMISSION_PATH, VALIDATION_REPORT_PATH
from procurement.output_validator import OutputValidator


def main():
    target_path = SUBMISSION_PATH
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])

    print(f"[*] Validating submission file: {target_path}")
    validator = OutputValidator()
    report = validator.validate_file(target_path)

    import json
    VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=" * 50)
    print("SUBMISSION VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Status       : {'PASSED' if report['is_valid'] else 'FAILED'}")
    print(f"Total Rows   : {report['total_rows']}")
    print(f"Action Counts: {report['action_counts']}")
    if report["errors"]:
        print(f"Errors ({len(report['errors'])}):")
        for err in report["errors"][:10]:
            print(f"  - {err}")
        if len(report["errors"]) > 10:
            print(f"  ... and {len(report['errors']) - 10} more errors.")
    print("=" * 50)

    if not report["is_valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
