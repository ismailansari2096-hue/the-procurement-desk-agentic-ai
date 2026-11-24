"""
Check volume discounts and list discounts across all 2000 threads.
"""

import sys
import csv
import re
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent

threads_path = root_dir / "data" / "raw" / "threads.csv"
with open(threads_path, "r", encoding="utf-8") as f:
    threads = list(csv.DictReader(f))

discount_pats = [
    re.compile(r"\b\d+%\s*off\b", re.I),
    re.compile(r"\bdiscount\b", re.I),
    re.compile(r"\bvolume\b", re.I),
    re.compile(r"\borders\s+of\b", re.I),
]

threads_with_discount = []
for t in threads:
    msg = t["supplier_message"]
    latest = msg.split("---")[-1].strip() if "---" in msg else msg.strip()
    for p in discount_pats:
        if p.search(latest):
            threads_with_discount.append((t["thread_id"], t["category"], t["supplier"], t["quantity"], latest.replace("\n", " ")))
            break

print(f"Total threads with discount mentions in latest message: {len(threads_with_discount)}")

# Categorize phrases
phrases = {}
for tid, cat, supp, qty, txt in threads_with_discount:
    # find discount sentences
    for sent in txt.split("."):
        if any(p.search(sent) for p in discount_pats):
            s = sent.strip()
            # simplify numbers
            s_clean = re.sub(r"\d+", "N", s)
            phrases[s_clean] = phrases.get(s_clean, 0) + 1

print("\nTop Discount Phrasing Patterns:")
for ph, cnt in sorted(phrases.items(), key=lambda x: -x[1])[:20]:
    print(f"  ({cnt:02d}) {ph}")
