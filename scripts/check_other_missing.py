import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

threads = load_threads(Path("data/raw/threads.csv"))
orch = NegotiationOrchestrator(mode="v3")

missing_threads = []
for t in threads:
    tid = t["thread_id"]
    val_out, trace = orch.process_thread(t)
    if "MISSING_INFO" in val_out.label:
        latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
        missing_threads.append((t, latest_msg))

other_missing = []
for t, msg in missing_threads:
    # not unlisted currency
    if not re.search(r"\b(JPY|CAD|AED|AUD|CHF|SGD)\b", msg, re.I):
        other_missing.append((t["thread_id"], t["category"], msg.replace("\n", " -- ")))

print(f"Other MISSING_INFO count: {len(other_missing)}")
for tid, cat, msg in other_missing[:20]:
    print(f"[{tid}] ({cat}): {msg[:120]}")
