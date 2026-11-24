"""
Measures the exact impact of fixing:
1. Banned Exclusivity: "buy ... only from us" (9 threads)
2. GST Inclusion: "incl. GST", "incl GST", "GST included" without parentheses (30+ threads)
"""

import sys
import re
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

THREADS = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")
V2_CSV = BASE_DIR / "outputs" / "experimental" / "submission_v2.csv"

with open(V2_CSV, "r", encoding="utf-8") as f:
    V2_ROWS = list(csv.DictReader(f))

V2_PREDS = {r["thread_id"]: r["label"] for r in V2_ROWS}


def main():
    print("=" * 70)
    print("MEASURING IMPACT OF PLAYBOOK RULE REFINEMENTS")
    print("=" * 70)

    # 1. Exclusivity check
    excl_re = re.compile(r"buy\s+these\s+items\s+only\s+from\s+us|buy\s+only\s+from\s+us|purchase\s+only\s+from\s+us", re.I)
    excl_threads = []
    for t in THREADS:
        tid = t["thread_id"]
        latest = t["supplier_message"].split("[Earlier message")[0]
        if excl_re.search(latest):
            if "BANNED_TERM" not in V2_PREDS[tid] and "PROMPT_INJECTION" not in V2_PREDS[tid]:
                excl_threads.append((tid, V2_PREDS[tid], "ESCALATE:BANNED_TERM:"))

    print(f"\n[1] Exclusivity affected threads: {len(excl_threads)}")
    for item in excl_threads:
        print(f"  {item[0]}: {item[1]} -> {item[2]}")

    # 2. GST inclusion check
    # Current regex: (inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))
    # Refined regex: (inclusive\s+of\s+GST|including\s+GST|incl\.?\s+GST|GST\s+included)
    gst_broad = re.compile(r"(inclusive\s+of\s+GST|including\s+GST|incl\.?\s+GST|GST\s+included)", re.I)
    gst_old = re.compile(r"(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))", re.I)

    gst_new_matches = []
    for t in THREADS:
        tid = t["thread_id"]
        latest = t["supplier_message"].split("[Earlier message")[0]
        if gst_broad.search(latest) and not gst_old.search(latest):
            gst_new_matches.append(tid)

    print(f"\n[2] GST inclusion newly matched threads: {len(gst_new_matches)}")
    print(f"Threads: {gst_new_matches}")


if __name__ == "__main__":
    main()
