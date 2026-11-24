"""
Script to verify differential agreement between IndependentReferenceEvaluator and V3.
Evaluates all 2,000 threads and reports all disagreements in detail.
"""

import sys
import csv
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agentic.reference_evaluator import IndependentReferenceEvaluator


def run_differential():
    root = Path(__file__).resolve().parent.parent
    threads_path = root / "data" / "raw" / "threads.csv"
    v3_path = root / "outputs" / "experimental" / "submission_v3.csv"

    with open(threads_path, encoding="utf-8") as f:
        threads = list(csv.DictReader(f))

    with open(v3_path, encoding="utf-8") as f:
        v3 = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

    ref = IndependentReferenceEvaluator()
    matches = 0
    disagreements = []

    for t in threads:
        tid = t["thread_id"]
        v3_label = v3[tid]
        ref_label = ref.evaluate_thread(t)
        if v3_label == ref_label:
            matches += 1
        else:
            disagreements.append({
                "thread_id": tid,
                "v3_label": v3_label,
                "ref_label": ref_label,
                "thread": t
            })

    total = len(threads)
    print("=" * 70)
    print("V4 DIFFERENTIAL VERIFICATION REPORT (ReferenceEvaluator vs V3)")
    print("=" * 70)
    print(f"Total Threads Evaluated : {total}")
    print(f"Exact Agreement Count   : {matches}/{total} ({matches/total*100:.2f}%)")
    print(f"Disagreement Count      : {len(disagreements)}/{total} ({len(disagreements)/total*100:.2f}%)")
    print("=" * 70)

    if disagreements:
        print("\nFIRST 25 DISAGREEMENTS:")
        for idx, d in enumerate(disagreements[:25], 1):
            tid = d["thread_id"]
            v3_l = d["v3_label"]
            ref_l = d["ref_label"]
            t = d["thread"]
            cat = t["category"]
            supp = t["supplier"]
            rnd = t["round"]
            qty = t["quantity"]
            msg = t["supplier_message"].replace("\n", " ")
            print(f"[{idx}] {tid}: V3='{v3_l}' vs REF='{ref_l}' | {cat} | {supp} | Rnd {rnd} | Qty {qty}")
            print(f"    Message: {msg[-160:]}")
            print("-" * 70)

    return matches, disagreements


if __name__ == "__main__":
    run_differential()
