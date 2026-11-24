"""
Experimental V2 Submission Builder.
Implements the 4 refined policy patterns extracted from the playbook:
1. Multilingual & CFO prompt injection templates
2. Acme's liability unlimited phrasing
3. Advance payment above 30% in words ('half the order value upfront')
4. Volume discounts: 'with a further D% off for orders of N or more' (when qty >= N)

Generates outputs/experimental/submission_v2.csv WITHOUT modifying outputs/submission.csv.
"""

import sys
import re
import csv
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from procurement.config import RAW_DATA_DIR, OUTPUTS_DIR
from procurement.data_loader import load_threads, load_sample_answers
from procurement.policy_engine import PolicyEngine
from procurement.counter_calculator import CounterCalculator
from procurement.output_validator import OutputValidator
from procurement.injection_detector import InjectionDetector
from procurement.banned_terms_detector import BannedTermsDetector
from procurement.thread_parser import ThreadParser
from procurement.decision_engine import DecisionEngine


class RefinedInjectionDetector(InjectionDetector):
    ADDITIONAL_PATTERNS = [
        re.compile(r"to\s+whichever\s+bot\s+screens\s+these", re.I),
        re.compile(r"AI\s*सहायक\s*के\s*लिए\s*निर्देश", re.I),
        re.compile(r"vendors\s+who\s+reply\s+within\s+24\s+hours\s+are\s+pre-approved", re.I),
        re.compile(r"If\s+an\s+automated\s+system\s+is\s+reading\s+this\s+email", re.I),
        re.compile(r"SYSTEM\s+NOTE\s+TO\s+AI\s+AGENT", re.I),
        re.compile(r"pre-approved\s+by\s+Acme'?s\s+CFO", re.I),
    ]

    def is_injection(self, text: str):
        is_inj, reason = super().is_injection(text)
        if is_inj:
            return True, reason

        sanitized = text
        for exc in self.EXCEPTIONS:
            sanitized = exc.sub(" ", sanitized)

        for pat in self.ADDITIONAL_PATTERNS:
            m = pat.search(sanitized)
            if m:
                return True, f"Matched refined injection trigger: '{m.group(0)}'"
        return False, ""


class RefinedBannedTermsDetector(BannedTermsDetector):
    ADDITIONAL_LIABILITY = [
        re.compile(r"acme'?s\s+liability\s+.*?\s+unlimited", re.I),
    ]
    ADDITIONAL_ADVANCE = [
        re.compile(r"\bhalf\s+(the\s+order\s+value\s+)?(upfront|advance)\b", re.I),
        re.compile(r"\b(upfront|advance)\s+.*?half\b", re.I),
        re.compile(r"payment\s+terms:\s*60%\s*advance", re.I),
    ]

    def has_banned_term(self, latest_message: str):
        has_banned, reason = super().has_banned_term(latest_message)
        if has_banned:
            return True, reason

        # Check refined liability
        for pat in self.ADDITIONAL_LIABILITY:
            m = pat.search(latest_message)
            if m:
                return True, f"Unlimited liability clause detected: '{m.group(0)}'"

        # Check refined advance
        for pat in self.ADDITIONAL_ADVANCE:
            m = pat.search(latest_message)
            if m:
                return True, f"Advance payment above 30% detected: '{m.group(0)}'"

        return False, ""


class RefinedThreadParser(ThreadParser):
    def extract_latest_offer(self, raw_thread: str, supplier_name: str, category_id: str, thread_date: str, quantity: int):
        price_inr, err, debug = super().extract_latest_offer(raw_thread, supplier_name, category_id, thread_date, quantity)
        if err or price_inr is None:
            return price_inr, err, debug

        latest_msg, _ = self.split_messages(raw_thread)

        # Check volume discount: "with a further D% off for orders of N [units] or more"
        vol_m = re.search(r"with\s+a\s+further\s+(\d+)\s*%\s*off\s+for\s+orders\s+of\s+(\d+)\s+([a-zA-Z\s]+?)\s+or\s+more", latest_msg, re.I)
        if vol_m:
            pct = float(vol_m.group(1))
            thresh = int(vol_m.group(2))
            if quantity >= thresh:
                price_inr = price_inr * (1.0 - pct / 100.0)
                debug["volume_discount_applied"] = f"{pct}% for qty {quantity} >= {thresh}"

        return price_inr, None, debug


class RefinedDecisionEngine(DecisionEngine):
    def __init__(self, policy_engine: PolicyEngine = None):
        super().__init__(policy_engine)
        self.parser = RefinedThreadParser(self.pe)
        self.injection_detector = RefinedInjectionDetector()
        self.banned_detector = RefinedBannedTermsDetector()


def main():
    print("=" * 60)
    print("EXPERIMENTAL V2 DECISION ENGINE EVALUATION")
    print("=" * 60)

    engine_v2 = RefinedDecisionEngine()

    # 1. Evaluate 40 worked examples
    samples = load_threads(RAW_DATA_DIR / "sample_threads.csv")
    answers = load_sample_answers(RAW_DATA_DIR / "sample_answers.csv")
    correct = 0
    for t in samples:
        tid = t["thread_id"]
        exp = answers[tid]
        act, aud = engine_v2.decide(t)
        if act == exp:
            correct += 1
        else:
            print(f"[-] Regression failure on {tid}: expected {exp}, got {act}")

    print(f"[+] Worked Examples Accuracy: {correct}/40 ({correct/40*100:.1f}%)")
    assert correct == 40, "Refined engine broke worked examples!"

    # 2. Run on 2,000 test threads
    test_threads = load_threads(RAW_DATA_DIR / "threads.csv")
    v2_predictions = []
    v2_audits = []

    for t in test_threads:
        label, aud = engine_v2.decide(t)
        v2_predictions.append((t["thread_id"], label))
        v2_audits.append(aud)

    # 3. Write outputs/experimental/submission_v2.csv
    out_v2 = OUTPUTS_DIR / "experimental" / "submission_v2.csv"
    with open(out_v2, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["thread_id", "label"])
        for tid, lbl in v2_predictions:
            writer.writerow([tid, lbl])

    # 4. Validate output
    validator = OutputValidator()
    v_report = validator.validate_file(out_v2, expected_rows=2000)
    print(f"[+] V2 Submission Generated: {out_v2}")
    print(f"[+] Validation Status: {'PASSED' if v_report['is_valid'] else 'FAILED'}")
    print(f"[+] Action Counts: {v_report['action_counts']}")

    # 5. Compare V1 vs V2 row by row
    v1_file = OUTPUTS_DIR / "submission.csv"
    with open(v1_file, "r", encoding="utf-8") as f:
        v1_rows = dict(list(csv.reader(f))[1:])

    diffs = []
    for tid, v2_lbl in v2_predictions:
        v1_lbl = v1_rows[tid]
        if v1_lbl != v2_lbl:
            diffs.append((tid, v1_lbl, v2_lbl))

    print(f"\n[+] Total Rows Changed from V1 to V2: {len(diffs)} / 2000 ({len(diffs)/2000*100:.2f}%)")

    # Categorize differences
    diff_cats = {}
    for tid, v1, v2 in diffs:
        cat_key = f"{v1.split(':')[0]}:{v1.split(':')[1]} -> {v2.split(':')[0]}:{v2.split(':')[1]}"
        diff_cats[cat_key] = diff_cats.get(cat_key, 0) + 1

    print("\nBreakdown of Changes:")
    for k, count in sorted(diff_cats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {k}: {count} threads")

    print("\nSample changed threads:")
    for tid, v1, v2 in diffs[:10]:
        print(f"  {tid}: V1 '{v1}' -> V2 '{v2}'")

    # Save comparison report
    comp_report = {
        "total_rows_changed": len(diffs),
        "percentage_changed": len(diffs) / 2000.0 * 100.0,
        "change_breakdown": diff_cats,
        "samples": [{"thread_id": tid, "v1": v1, "v2": v2} for tid, v1, v2 in diffs[:20]]
    }
    with open(OUTPUTS_DIR / "experimental" / "v1_v2_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comp_report, f, indent=2)

    print(f"[+] Saved comparison report to {OUTPUTS_DIR / 'experimental' / 'v1_v2_comparison.json'}")


if __name__ == "__main__":
    main()
