import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

threads = load_threads(Path("data/raw/threads.csv"))
target_tids = ['T10048', 'T10156', 'T10287', 'T10290', 'T10421', 'T10591', 'T10639', 'T11710']

orch_v2 = NegotiationOrchestrator(mode="v2")

for tid in target_tids:
    t = next(x for x in threads if x["thread_id"] == tid)
    v2_val, trace = orch_v2.process_thread(t)
    latest_msg, _ = orch_v2.thread_agent.parser.split_messages(t["supplier_message"])
    cat = t["category"]
    eff_pol = trace["policy_compliance"]
    
    print(f"\n==================== {tid} ====================")
    print(f"Category: {cat} | Qty: {t['quantity']} | Round: {t['round']}/{eff_pol.effective_rounds} | Date: {t['date']}")
    print(f"Target: {eff_pol.effective_target} | Walkaway: {eff_pol.effective_walkaway} | Approval: {eff_pol.effective_approval_limit}")
    print(f"Supplier: {t['supplier']} (Probation={eff_pol.is_probation})")
    for line in latest_msg.split("\n"):
        if "gst" in line.lower() or "price" in line.lower() or "offer" in line.lower() or "quote" in line.lower():
            print(f"Quote line: {line.strip()}")
    print(f"V2 Decision: {v2_val.label} (Fired Step: {v2_val.fired_step})")
