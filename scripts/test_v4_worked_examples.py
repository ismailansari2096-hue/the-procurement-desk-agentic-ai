"""
Verify NegotiationOrchestrator(mode="v4") passes all 40 competition worked examples.
"""

import sys
import csv
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from agentic.orchestrator import NegotiationOrchestrator

def main():
    samples_path = root_dir / "data" / "raw" / "sample_threads.csv"
    with open(samples_path, "r", encoding="utf-8") as f:
        samples = list(csv.DictReader(f))

    answers_path = root_dir / "data" / "raw" / "sample_answers.csv"
    with open(answers_path, "r", encoding="utf-8") as f:
        answers = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

    orch = NegotiationOrchestrator(mode="v4")
    passed = 0
    failures = []

    for s in samples:
        tid = s["thread_id"]
        expected = answers[tid]
        actual = orch.decide(s)
        if actual == expected:
            passed += 1
        else:
            failures.append((tid, expected, actual))

    print(f"Worked Examples Passed: {passed} / {len(samples)} ({passed/len(samples)*100:.1f}%)")
    if failures:
        print("Failures:")
        for tid, exp, act in failures:
            print(f"  {tid}: expected {exp}, got {act}")
        sys.exit(1)
    else:
        print("ALL 40 WORKED EXAMPLES PASSED PERFECTLY!")

if __name__ == "__main__":
    main()
