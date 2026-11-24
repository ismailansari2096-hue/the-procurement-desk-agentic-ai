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

tiered_threads = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    if "orders of up to" in latest_msg.lower() or "larger orders" in latest_msg.lower():
        val_out, trace = orch.process_thread(t)
        tiered_threads.append((tid, t["category"], t["quantity"], val_out.label, latest_msg))

print(f"Total tiered pricing threads: {len(tiered_threads)}")
for tid, cat, qty, label, msg in tiered_threads:
    for line in msg.split("\n"):
        if "orders of up to" in line.lower():
            print(f"[{tid}] ({cat}, Qty {qty}) -> {label} | Line: {line.strip()}")
