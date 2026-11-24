import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads

threads = load_threads(Path("data/raw/threads.csv"))

non_ascii_threads = []
standard_non_ascii = set("—–’“”₹€£…")

for t in threads:
    tid = t["thread_id"]
    msg = t["supplier_message"]
    unusual_chars = set()
    for ch in msg:
        if ord(ch) > 127 and ch not in standard_non_ascii:
            unusual_chars.add(ch)
    if unusual_chars:
        # Check if devanagari
        is_devanagari = all(0x0900 <= ord(c) <= 0x097F for c in unusual_chars)
        non_ascii_threads.append((tid, is_devanagari, unusual_chars, msg))

print(f"Total threads with non-ASCII beyond standard currency/punctuation: {len(non_ascii_threads)}")
non_devanagari = [x for x in non_ascii_threads if not x[1]]
print(f"Threads with NON-Devanagari unusual characters: {len(non_devanagari)}")
for tid, is_dev, chars, msg in non_devanagari:
    print(f"[{tid}] Chars: {chars} | Msg: {msg[:100]}")
