import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads

threads = load_threads(Path("data/raw/threads.csv"))

patterns = [
    re.compile(r"\b\d+\s*%\s*(?:off|discount)[^\n]*(?:previous|earlier|last|prior)\b", re.I),
    re.compile(r"\b(?:previous|earlier|last|prior)\s*(?:quote|price|offer)[^\n]*\d+\s*%\b", re.I),
]

matches = []
for t in threads:
    tid = t["thread_id"]
    msg = t["supplier_message"]
    for pat in patterns:
        m = pat.search(msg)
        if m:
            matches.append((tid, m.group(0), msg))
            break

print(f"Total threads matching earlier quote discount patterns: {len(matches)}")
for tid, snippet, msg in matches[:20]:
    print(f"[{tid}]: Snippet: '{snippet}'")
