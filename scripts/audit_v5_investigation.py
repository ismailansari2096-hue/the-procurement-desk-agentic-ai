"""
Comprehensive audit script for V5 investigation.
Compares V4 predictions against IndependentReferenceEvaluator and checks all potential policy edge cases.
"""

import sys
import csv
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from agentic.orchestrator import NegotiationOrchestrator
from agentic.reference_evaluator import IndependentReferenceEvaluator


def main():
    threads_path = root_dir / "data" / "raw" / "threads.csv"
    with open(threads_path, "r", encoding="utf-8") as f:
        threads = list(csv.DictReader(f))

    v4_path = root_dir / "outputs" / "experimental" / "submission_v4.csv"
    with open(v4_path, "r", encoding="utf-8") as f:
        v4_rows = list(csv.DictReader(f))
    v4_dict = {r["thread_id"]: r["label"] for r in v4_rows}

    orch_v4 = NegotiationOrchestrator(mode="v4")
    ref_eval = IndependentReferenceEvaluator()

    discrepancies = []
    ref_matches = 0

    for t in threads:
        tid = t["thread_id"]
        v4_label = v4_dict[tid]
        
        # Cross check with fresh orchestrator run
        orch_label = orch_v4.decide(t)
        assert orch_label == v4_label, f"Mismatch in V4 re-run for {tid}: {orch_label} vs {v4_label}"

        # Reference evaluator
        ref_label = ref_eval.evaluate_thread(t)
        if ref_label != v4_label:
            discrepancies.append({
                "thread_id": tid,
                "category": t["category"],
                "supplier": t["supplier"],
                "round": t["round"],
                "quantity": t["quantity"],
                "date": t["date"],
                "v4_label": v4_label,
                "ref_label": ref_label,
                "msg": t["supplier_message"].replace("\n", " ")
            })
        else:
            ref_matches += 1

    print(f"Total Threads: {len(threads)}")
    print(f"V4 matches Reference Evaluator: {ref_matches} / {len(threads)} ({ref_matches/len(threads)*100:.2f}%)")
    print(f"Discrepancies found: {len(discrepancies)}")

    if discrepancies:
        print("\nFIRST 20 DISCREPANCIES:")
        for idx, d in enumerate(discrepancies[:20], 1):
            print(f"[{idx:02d}] {d['thread_id']} ({d['category']}, {d['supplier']}, Rnd {d['round']}, Qty {d['quantity']}):")
            print(f"     V4 : {d['v4_label']}")
            print(f"     REF: {d['ref_label']}")
            print(f"     Msg: {d['msg'][-120:]}")
            print("-" * 65)


if __name__ == "__main__":
    main()
