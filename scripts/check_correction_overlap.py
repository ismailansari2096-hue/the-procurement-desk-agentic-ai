import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads

threads = load_threads(Path("data/raw/threads.csv"))

overlap_threads = []
for t in threads:
    tid = t["thread_id"]
    msg = t["supplier_message"]
    has_corr = "correction" in msg.lower()
    has_earlier_disc = bool(re.search(r"\b\d+\s*%\s*(?:discount\s+on|off)\s+our\s+previous\s+quote", msg, re.I))
    if has_corr and has_earlier_disc:
        overlap_threads.append((tid, msg))

print(f"Threads with BOTH correction and earlier quote discount: {len(overlap_threads)}")
for tid, msg in overlap_threads:
    print(f"[{tid}]: {msg.replace(chr(10), ' -- ')[:200]}")
