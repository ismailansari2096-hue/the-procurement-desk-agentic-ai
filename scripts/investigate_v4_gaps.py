import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

BASE_DIR = Path(".")
threads = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")
orch = NegotiationOrchestrator(mode="v3")

with open("outputs/experimental/submission_v3.csv", "r", encoding="utf-8") as f:
    v3_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

print(f"Total threads loaded: {len(threads)}")

# 1. Investigate FREE UNITS (Precedents P-02, P-05)
print("\n=== 1. AUDITING FREE UNITS / CONCESSIONS (P-02, P-05) ===")
free_pat = re.compile(r"\b(free|bonus|complimentary|buy\s+\d+\s+get)\b", re.I)
free_matches = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    m = free_pat.search(latest_msg)
    if m:
        free_matches.append((tid, t["category"], t["quantity"], v3_preds[tid], latest_msg))

print(f"Total threads with free/bonus terms in latest msg: {len(free_matches)}")
for tid, cat, qty, pred, msg in free_matches[:15]:
    for line in msg.split("\n"):
        if any(w in line.lower() for w in ["free", "bonus", "complimentary", "get"]):
            print(f"[{tid}] ({cat}, Qty {qty}) -> V3: {pred} | Line: {line.strip()}")

# 2. Investigate RANGES (Precedents P-01, P-04)
print("\n=== 2. AUDITING PRICE RANGES (P-01, P-04) ===")
range_pat = re.compile(r"\b(between\s+[^\n]+and|from\s+[^\n]+to\s+\d+|[₹$€£\d,]+\s*-\s*[₹$€£\d,]+)\b", re.I)
range_matches = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    m = range_pat.search(latest_msg)
    if m:
        range_matches.append((tid, t["category"], v3_preds[tid], latest_msg))

print(f"Total threads with potential price ranges: {len(range_matches)}")
for tid, cat, pred, msg in range_matches[:10]:
    for line in msg.split("\n"):
        if any(w in line.lower() for w in ["between", "from", "-"]):
            print(f"[{tid}] ({cat}) -> V3: {pred} | Line: {line.strip()}")

# 3. Investigate OTHER VOLUME DISCOUNT WORDINGS
print("\n=== 3. AUDITING VOLUME DISCOUNT PHRASES ===")
vol_broad_pat = re.compile(r"(discount|off\b|threshold|bulk|tier|volume|order\s+of\s+\d+|orders\s+of\s+\d+)", re.I)
vol_existing_regex = re.compile(
    r"with\s+a\s+further\s+(\d+)\s*%\s*off\s+for\s+orders\s+of\s+(\d+)\s+([a-zA-Z\s]+?)\s+or\s+more",
    re.I
)
unmatched_vol = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    if vol_broad_pat.search(latest_msg) and not vol_existing_regex.search(latest_msg):
        # check if there's any discount mentioned
        for line in latest_msg.split("\n"):
            if any(w in line.lower() for w in ["discount", "% off", "bulk", "tier"]):
                unmatched_vol.append((tid, t["category"], t["quantity"], v3_preds[tid], line.strip()))

print(f"Total lines with discount keywords not caught by existing VOL regex: {len(unmatched_vol)}")
for tid, cat, qty, pred, line in unmatched_vol[:20]:
    print(f"[{tid}] ({cat}, Qty {qty}) -> V3: {pred} | {line}")

# 4. Investigate SUPPLIER CONTRACTS / AMENDMENTS
print("\n=== 4. AUDITING SUPPLIER CONTRACTS & AMENDMENTS ===")
pe = orch.pe
print(f"Categories: {list(pe.categories.keys())}")
print(f"Amendments count: {len(pe.amendments)}")
print(f"Suppliers count: {len(pe.suppliers)}")
for s_name, s_data in pe.suppliers.items():
    print(f"  Supplier: {s_name} -> {s_data}")
