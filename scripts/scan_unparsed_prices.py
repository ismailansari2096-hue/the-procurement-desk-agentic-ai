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

print("=== 1. AUDITING ALL 91 MISSING_INFO THREADS ===")
missing_threads = []
for t in threads:
    tid = t["thread_id"]
    val_out, trace = orch.process_thread(t)
    if "MISSING_INFO" in val_out.label:
        latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
        missing_threads.append((t, latest_msg))

print(f"Total MISSING_INFO threads: {len(missing_threads)}")

# Check if any of these 91 actually contain a usable price
currencies_table = {"USD", "EUR", "GBP", "INR", "RS", "RS.", "₹", "$", "€", "£"}
potential_missed_prices = []
for t, msg in missing_threads:
    tid = t["thread_id"]
    cat = t["category"]
    # Check if there is any number that looks like a price
    has_num = bool(re.search(r"\b\d{2,}(?:,\d{3})*(?:\.\d+)?\b", msg))
    # Check if currency mentioned
    has_curr = bool(re.search(r"\b(INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP|JPY|CAD|AED|AUD|CHF|SGD)\b", msg, re.I))
    # Check if call us / phone
    is_call = bool(re.search(r"\b(call|phone|discuss|specs|details)\b", msg, re.I))
    
    # If it has a number AND a recognized currency, why did it become MISSING_INFO?
    if has_num and has_curr:
        potential_missed_prices.append((tid, cat, t["supplier"], msg.replace("\n", " -- ")))

print(f"MISSING_INFO threads with number and currency: {len(potential_missed_prices)}")
for tid, cat, supp, msg in potential_missed_prices[:25]:
    print(f"[{tid}] ({cat}, {supp}): {msg[:150]}")
