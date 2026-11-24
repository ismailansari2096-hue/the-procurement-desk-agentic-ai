"""
Check all threads containing words-as-numbers to ensure full coverage and correct currency/unit handling.
"""

import sys
import csv
import re
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent

threads_path = root_dir / "data" / "raw" / "threads.csv"
with open(threads_path, "r", encoding="utf-8") as f:
    threads = list(csv.DictReader(f))

word_tokens_sorted = r"(?:thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|lakh|lakhs|twelve|eleven|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
clean_pat = re.compile(rf"(?:is|quote|offer|can do|at)\s+({word_tokens_sorted}+(?:\s+(?:and\s+)?{word_tokens_sorted}+)*)\s*([a-zA-Z\s\./]+)?", re.I)

word_threads = []
for t in threads:
    tid = t["thread_id"]
    msg = t["supplier_message"]
    latest = msg.split("---")[-1].strip() if "---" in msg else msg.strip()
    has_digit = bool(re.search(r"(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)\s*[\d,]+(?:\.\d+)?", latest))
    clean_msg = latest.replace("-", " ")
    m = clean_pat.search(clean_msg)
    if m:
        word_threads.append({
            "tid": tid,
            "has_digit": has_digit,
            "words": m.group(1),
            "tail": m.group(2) or "",
            "latest": latest
        })

print(f"Total threads matching word pattern: {len(word_threads)}")
pure_word_threads = [wt for wt in word_threads if not wt["has_digit"]]
print(f"Pure word threads (no digit price): {len(pure_word_threads)}")

currencies_seen = set()
for wt in pure_word_threads:
    tail = wt["tail"].lower()
    for curr in ["dollar", "usd", "euro", "eur", "pound", "gbp", "sgd", "aed"]:
        if curr in tail:
            currencies_seen.add(curr)

print(f"Foreign currencies seen in pure word threads: {currencies_seen}")
