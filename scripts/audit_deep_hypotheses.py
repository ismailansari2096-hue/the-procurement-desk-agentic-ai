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

with open("outputs/experimental/submission_v3.csv") as f:
    v3_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

print("=== DEEP HYPOTHESES SCAN ===")

# 1. Supplier offer <= our_last_counter
counter_crossings = []
for t in threads:
    tid = t["thread_id"]
    olc = t.get("our_last_counter")
    if olc is not None and str(olc).strip() != "" and str(olc).strip() != "nan":
        try:
            olc_val = float(olc)
        except ValueError:
            continue
        val_out, trace = orch.process_thread(t)
        tu = trace["thread_understanding"]
        if tu.effective_inr_price is not None and not tu.is_missing_info:
            if tu.effective_inr_price <= olc_val:
                counter_crossings.append((tid, t["category"], t["round"], olc_val, tu.effective_inr_price, val_out.label))

print(f"Threads where supplier offer <= our_last_counter: {len(counter_crossings)}")
for item in counter_crossings[:10]:
    print(f"[{item[0]}] ({item[1]}, Rnd {item[2]}): Our Last Counter={item[3]} vs Supplier Offer={item[4]} -> V3: {item[5]}")

# 2. Verbal / Prior agreement mentions
verbal_threads = []
for t in threads:
    tid = t["thread_id"]
    msg = t["supplier_message"]
    if re.search(r"\b(verbal|verbally|mutually\s+agreed|prior\s+discussion|as\s+discussed)\b", msg, re.I):
        val_out, _ = orch.process_thread(t)
        verbal_threads.append((tid, val_out.label, msg[:100].replace("\n", " ")))

print(f"\nThreads mentioning verbal/prior discussion: {len(verbal_threads)}")
for item in verbal_threads[:10]:
    print(f"[{item[0]}] -> V3: {item[1]} | {item[2]}")

# 3. Check distribution of V3 labels
print("\n=== V3 LABEL DISTRIBUTION (2,000 THREADS) ===")
label_counts = {}
for r in v3_preds.values():
    action = r.split(":")[0]
    reason = r.split(":")[1]
    key = f"{action}:{reason}"
    label_counts[key] = label_counts.get(key, 0) + 1

for k, v in sorted(label_counts.items(), key=lambda x: -x[1]):
    print(f"  {k:35}: {v} ({v/2000*100:.2f}%)")
