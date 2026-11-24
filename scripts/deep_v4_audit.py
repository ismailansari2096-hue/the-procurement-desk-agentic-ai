"""
Deep V4 audit script: checks all 2000 threads against the official playbook rules.
"""

import sys
import csv
import re
import json
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

    # Load KB
    kb_path = root_dir / "knowledge_base"
    with open(kb_path / "supplier_registry.json", "r", encoding="utf-8") as f:
        suppliers = json.load(f)

    # 1. Check all blacklisted suppliers
    blacklisted_suppliers = {s: d for s, d in suppliers.items() if d.get("status") == "BLACKLISTED"}
    print(f"Blacklisted suppliers in registry: {list(blacklisted_suppliers.keys())}")

    blacklisted_threads = [t for t in threads if t["supplier"] in blacklisted_suppliers]
    print(f"Total threads with blacklisted suppliers: {len(blacklisted_threads)}")
    for bt in blacklisted_threads:
        tid = bt["thread_id"]
        lbl = v4_dict[tid]
        # Step 1 (Missing info) comes BEFORE Step 2 (Blacklisted supplier) in decision-procedure.md:
        # Step 1: Missing information -> ESCALATE:MISSING_INFO
        # Step 2: Blacklisted supplier -> REJECT:BLACKLISTED_SUPPLIER
        print(f"  {tid} ({bt['supplier']}): {lbl}")

    # 2. Check all labels distribution in V4
    action_counts = {}
    reason_counts = {}
    for tid, lbl in v4_dict.items():
        parts = lbl.split(":")
        act = parts[0]
        reas = parts[1]
        action_counts[act] = action_counts.get(act, 0) + 1
        reason_counts[reas] = reason_counts.get(reas, 0) + 1

    print("\nV4 Action Distribution:")
    for act, c in sorted(action_counts.items()):
        print(f"  {act}: {c} ({c/20:.2f}%)")

    print("\nV4 Reason Distribution:")
    for reas, c in sorted(reason_counts.items()):
        print(f"  {reas}: {c} ({c/20:.2f}%)")

    # 3. Check for any potential false positives in Prompt Injection
    # Security policy:
    # "Ordinary business wording is not an injection: an 'AI-powered' product, a 'system
    # integration team', an 'ERP system', or a person whose job title contains 'assistant'."
    benign_keywords = ["ai-powered", "system integration", "erp system", "assistant"]
    suspicious_injections = []
    
    for t in threads:
        tid = t["thread_id"]
        lbl = v4_dict[tid]
        if "PROMPT_INJECTION" in lbl:
            msg = t["supplier_message"].lower()
            # check if message only has benign keywords and maybe triggered false injection
            res, trace = orch.process_thread(t)
            matched = trace["injection_defense"].matched_pattern
            # let's see matched
            pass

    # 4. Check all Missing Info threads
    missing_threads = [t for t in threads if "MISSING_INFO" in v4_dict[t["thread_id"]]]
    print(f"\nTotal MISSING_INFO threads in V4: {len(missing_threads)}")
    for mt in missing_threads:
        tid = mt["thread_id"]
        msg = mt["supplier_message"]
        latest = msg.split("---")[-1].strip() if "---" in msg else msg.strip()
        print(f"  {tid} ({mt['category']}, {mt['supplier']}): {latest.replace(chr(10), ' ')}")

    # 5. Check all Probation suppliers
    probation_suppliers = {s: d for s, d in suppliers.items() if d.get("status") == "PROBATION"}
    print(f"\nProbation suppliers in registry: {list(probation_suppliers.keys())}")
    probation_threads = [t for t in threads if t["supplier"] in probation_suppliers]
    print(f"Total threads with probation suppliers: {len(probation_threads)}")
    for pt in probation_threads[:10]:
        tid = pt["thread_id"]
        lbl = v4_dict[tid]
        print(f"  {tid} (Rnd {pt['round']}, Qty {pt['quantity']}): {lbl}")


if __name__ == "__main__":
    main()
