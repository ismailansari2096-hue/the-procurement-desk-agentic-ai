"""
Audit all prompt injections in V4.
"""

import sys
import csv
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from agentic.orchestrator import NegotiationOrchestrator

def main():
    threads_path = root_dir / "data" / "raw" / "threads.csv"
    with open(threads_path, "r", encoding="utf-8") as f:
        threads = list(csv.DictReader(f))

    v4_path = root_dir / "outputs" / "experimental" / "submission_v4.csv"
    with open(v4_path, "r", encoding="utf-8") as f:
        v4_rows = list(csv.DictReader(f))
    v4_dict = {r["thread_id"]: r["label"] for r in v4_rows}

    orch = NegotiationOrchestrator(mode="v4")

    injections = []
    for t in threads:
        tid = t["thread_id"]
        lbl = v4_dict[tid]
        if "PROMPT_INJECTION" in lbl:
            res, trace = orch.process_thread(t)
            inj_output = trace["injection_defense"]
            injections.append({
                "thread_id": tid,
                "category": t["category"],
                "supplier": t["supplier"],
                "attack_cat": inj_output.attack_category,
                "matched": inj_output.matched_pattern,
                "full_thread": t["supplier_message"]
            })

    print(f"Total PROMPT_INJECTION in V4: {len(injections)}")
    cat_counts = {}
    for inj in injections:
        cat_counts[inj["attack_cat"]] = cat_counts.get(inj["attack_cat"], 0) + 1
    for cat, cnt in sorted(cat_counts.items()):
        print(f"  {cat}: {cnt}")

    # Check non-injections to see if any injection patterns might have been missed
    missed_candidates = []
    suspicious_words = [
        r"ignore\s+previous",
        r"system\s+prompt",
        r"developer\s+mode",
        r"admin\s+override",
        r"jailbreak",
        r"disregard\s+prior",
        r"act\s+as\s+",
        r"you\s+must\s+accept",
        r"cfo\s+approved",
        r"bypass",
        r"pre-approved",
        r"to\s+whichever\s+bot",
        r"ai\s+agent",
        r"ai\s+model",
        r"language\s+model"
    ]
    import re
    comb_pat = re.compile("|".join(suspicious_words), re.I)

    for t in threads:
        tid = t["thread_id"]
        lbl = v4_dict[tid]
        if "PROMPT_INJECTION" not in lbl:
            msg = t["supplier_message"]
            m = comb_pat.search(msg)
            if m:
                missed_candidates.append((tid, lbl, m.group(0), msg[-150:].replace("\n", " ")))

    print(f"\nNon-injection threads containing suspicious words: {len(missed_candidates)}")
    for tid, lbl, match_w, excerpt in missed_candidates[:15]:
        print(f"  {tid} [{lbl}] matched '{match_w}': {excerpt}")

if __name__ == "__main__":
    main()
