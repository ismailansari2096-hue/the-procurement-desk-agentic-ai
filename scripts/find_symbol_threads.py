import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads

threads = load_threads(Path("data/raw/threads.csv"))

euro_symbol_threads = []
pound_symbol_threads = []
correction_threads = []

for t in threads:
    tid = t["thread_id"]
    msg = t["supplier_message"]
    if "€" in msg:
        euro_symbol_threads.append((tid, msg))
    if "£" in msg:
        pound_symbol_threads.append((tid, msg))
    if "correction" in msg.lower():
        correction_threads.append((tid, msg))

print(f"Threads with '€' (Euro symbol): {len(euro_symbol_threads)}")
print(f"Threads with '£' (Pound symbol): {len(pound_symbol_threads)}")
print(f"Threads with 'correction': {len(correction_threads)}")

# Inspect sample of each
if euro_symbol_threads:
    print("\nSample Euro symbol threads:")
    for tid, msg in euro_symbol_threads[:5]:
        print(f"  [{tid}]: {msg[:100].replace(chr(10), ' ')}")

if pound_symbol_threads:
    print("\nSample Pound symbol threads:")
    for tid, msg in pound_symbol_threads[:5]:
        print(f"  [{tid}]: {msg[:100].replace(chr(10), ' ')}")

if correction_threads:
    print("\nSample Correction threads:")
    for tid, msg in correction_threads[:5]:
        print(f"  [{tid}]: {msg[:100].replace(chr(10), ' ')}")
