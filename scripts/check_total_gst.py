import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads

threads = load_threads(Path("data/raw/threads.csv"))

total_gst_threads = []
for t in threads:
    latest = t["supplier_message"].split("Earlier message")[-1]
    if re.search(r"in\s+total\s+for\s+all", latest, re.I) and re.search(r"\bgst\b", latest, re.I):
        total_gst_threads.append((t["thread_id"], latest))

print(f"Threads with BOTH total for all and GST: {len(total_gst_threads)}")
for tid, msg in total_gst_threads:
    print(f"[{tid}]: {msg.replace(chr(10), ' -- ')[:150]}")
