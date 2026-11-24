"""
Worked Example Evaluator.
Evaluates DecisionEngine against all 40 ground truth worked examples from sample_answers.csv.
Reports exact-match accuracy, action accuracy, reason accuracy, and counter-price accuracy.
"""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from procurement.config import RAW_DATA_DIR
from procurement.data_loader import load_threads, load_sample_answers
from procurement.decision_engine import DecisionEngine


def evaluate():
    threads = load_threads(RAW_DATA_DIR / "sample_threads.csv")
    answers = load_sample_answers(RAW_DATA_DIR / "sample_answers.csv")
    engine = DecisionEngine()

    total = len(threads)
    exact_matches = 0
    action_matches = 0
    reason_matches = 0
    price_matches = 0
    total_counters = 0

    mismatches = []

    for t in threads:
        tid = t["thread_id"]
        expected = answers[tid]
        actual, audit = engine.decide(t)

        exp_act, exp_reas, exp_price = expected.split(":")
        act_act, act_reas, act_price = actual.split(":")

        is_exact = (actual == expected)
        if is_exact:
            exact_matches += 1
        else:
            mismatches.append((tid, expected, actual, audit))

        if exp_act == act_act:
            action_matches += 1
        if exp_reas == act_reas:
            reason_matches += 1
        if exp_act == "COUNTER":
            total_counters += 1
            if exp_price == act_price:
                price_matches += 1

    print("=" * 60)
    print("WORKED EXAMPLES EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Examples Evaluated   : {total}")
    print(f"Exact Match Accuracy       : {exact_matches}/{total} ({exact_matches/total*100:.2f}%)")
    print(f"Action-Level Accuracy      : {action_matches}/{total} ({action_matches/total*100:.2f}%)")
    print(f"Reason-Level Accuracy      : {reason_matches}/{total} ({reason_matches/total*100:.2f}%)")
    if total_counters > 0:
        print(f"Counter Price Accuracy     : {price_matches}/{total_counters} ({price_matches/total_counters*100:.2f}%)")
    print("=" * 60)

    if mismatches:
        print(f"Mismatches ({len(mismatches)}):")
        for tid, exp, act, aud in mismatches:
            print(f"  {tid}: Expected '{exp}' | Got '{act}' (Step {aud.get('fired_step')})")
        sys.exit(1)
    else:
        print("[+] PERFECT 100% REGRESSION ACCURACY ACHIEVED!")


if __name__ == "__main__":
    evaluate()
