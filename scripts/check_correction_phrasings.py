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

corr_threads = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, earlier_msgs = orch.thread_agent.parser.split_messages(t["supplier_message"])
    if "correction" in latest_msg.lower():
        val_out, trace = orch.process_thread(t)
        corr_threads.append((tid, t["category"], val_out.label, latest_msg))

print(f"Total threads with 'correction' in LATEST message: {len(corr_threads)}")
for tid, cat, label, msg in corr_threads[:15]:
    for line in msg.split("\n"):
        if "correction" in line.lower():
            print(f"[{tid}] ({cat}) -> {label} | Line: {line.strip()}")
