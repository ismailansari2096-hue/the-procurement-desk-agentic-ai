import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

threads = load_threads(Path("data/raw/threads.csv"))
orch = NegotiationOrchestrator(mode="v3")

boundary_threads = []
for t in threads:
    tid = t["thread_id"]
    val_out, trace = orch.process_thread(t)
    tu = trace["thread_understanding"]
    pn = trace["pricing_negotiation"]
    if tu.effective_inr_price is not None and not tu.is_missing_info:
        diff = abs(tu.effective_inr_price - pn.concession_level)
        if diff < 5.0:
            boundary_threads.append((tid, t["category"], t["round"], tu.effective_inr_price, pn.concession_level, diff, val_out.label))

print(f"Total threads within 5 INR of concession level: {len(boundary_threads)}")
for item in boundary_threads:
    print(f"[{item[0]}] ({item[1]}, Rnd {item[2]}) p={item[3]:.2f} vs L(r)={item[4]:.2f} (diff={item[5]:.2f}) -> {item[6]}")
