import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

threads = load_threads(Path("data/raw/threads.csv"))
orch = NegotiationOrchestrator(mode="v3")

with open("outputs/experimental/submission_v3.csv", "r", encoding="utf-8") as f:
    v3_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

sample_ids = ["T10094", "T10229", "T10265", "T10475"]
for tid in sample_ids:
    t = next(x for x in threads if x["thread_id"] == tid)
    val_out, trace = orch.process_thread(t)
    tu = trace["thread_understanding"]
    print(f"\n[{tid}] ({t['category']}) -> V3 Label: {v3_preds[tid]}")
    print(f"  Parsed Price INR: {tu.effective_inr_price}")
    print(f"  Detected Currency: {tu.currency}")
    print(f"  Latest Msg Line:")
    for line in tu.latest_message.split("\n"):
        if any(sym in line for sym in ["€", "£", "EUR", "GBP"]):
            print(f"    {line.strip()}")
