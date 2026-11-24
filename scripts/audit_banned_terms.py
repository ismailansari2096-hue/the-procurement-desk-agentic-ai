"""
Audit all banned contract terms across all 2000 threads.
"""

import sys
import csv
import re
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

    banned_threads = []
    for t in threads:
        tid = t["thread_id"]
        lbl = v4_dict[tid]
        if "BANNED_TERM" in lbl:
            res, trace = orch.process_thread(t)
            pol_out = trace["policy_compliance"]
            banned_threads.append({
                "thread_id": tid,
                "category": t["category"],
                "supplier": t["supplier"],
                "reason": pol_out.banned_term_reason,
                "clause": pol_out.banned_term_clause,
                "msg": trace["thread_understanding"].latest_message.replace("\n", " ")
            })

    print(f"Total BANNED_TERM in V4: {len(banned_threads)}")
    for bt in banned_threads[:15]:
        print(f"  {bt['thread_id']} ({bt['category']}, {bt['supplier']}): {bt['reason']}")

    # Check non-banned threads for any potential missed banned terms in latest message
    banned_pats = [
        ("auto-renew", re.compile(r"auto-renew|renews\s+on\s+its\s+own|continues\s+year\s+to\s+year|continues\s+from\s+year\s+to\s+year", re.I)),
        ("advance>30%", re.compile(r"\b(?:[3-9]\d|100)%\s*(?:advance|upfront)|\b(?:half|quarter|third|two-thirds)\s+(?:the\s+order\s+value\s+)?(?:upfront|advance)\b", re.I)),
        ("unlimited liability", re.compile(r"liability\s+.*?\s+unlimited", re.I)),
        ("exclusivity", re.compile(r"buy\s+only\s+from|exclusive\s+supplier|exclusivity", re.I))
    ]

    missed_candidates = []
    for t in threads:
        tid = t["thread_id"]
        lbl = v4_dict[tid]
        # In decision hierarchy, Step 1 (Missing info), Step 2 (Blacklisted), Step 3 (Prompt injection)
        # come BEFORE Step 4 (Banned terms). If label is one of those, it wouldn't be BANNED_TERM.
        # But if label is ACCEPT, COUNTER, REJECT:ABOVE_WALKAWAY, or ESCALATE:OVER_APPROVAL_LIMIT,
        # it reached Step 5/6, so if it had a banned term, that would be a bug!
        if any(prefix in lbl for prefix in ["ACCEPT", "COUNTER", "ABOVE_WALKAWAY", "OVER_APPROVAL_LIMIT"]):
            msg = t["supplier_message"]
            latest = msg.split("---")[-1].strip() if "---" in msg else msg.strip()
            # check latest message
            for name, pat in banned_pats:
                m = pat.search(latest)
                if m:
                    missed_candidates.append((tid, lbl, name, m.group(0), latest[-150:].replace("\n", " ")))

    print(f"\nNon-banned threads reaching Step 5/6 matching banned patterns: {len(missed_candidates)}")
    for tid, lbl, name, match_w, excerpt in missed_candidates:
        print(f"  {tid} [{lbl}] matched '{name}' ('{match_w}'): {excerpt}")

if __name__ == "__main__":
    main()
