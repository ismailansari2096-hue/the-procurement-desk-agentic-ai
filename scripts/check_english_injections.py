import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads

threads = load_threads(Path("data/raw/threads.csv"))
with open("outputs/experimental/submission_v3.csv", "r", encoding="utf-8") as f:
    v3_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

# Patterns that might indicate prompt injection
inj_patterns = [
    re.compile(r"\b(ignore\s+(?:all\s+)?previous\s+instructions|disregard\s+prior)\b", re.I),
    re.compile(r"\b(system\s+prompt|new\s+instructions?|system\s+directive)\b", re.I),
    re.compile(r"\b(admin\s+override|executive\s+override|management\s+override)\b", re.I),
    re.compile(r"\b(pre[- ]approved|already\s+approved|prior\s+approval)\b", re.I),
    re.compile(r"\b(cfo|ceo|board)\s+(?:has\s+)?approved\b", re.I),
    re.compile(r"\b(you\s+must\s+accept|must\s+be\s+accepted|mandatory\s+approval)\b", re.I),
    re.compile(r"\b(bot|crawler|automated\s+agent|language\s+model|llm|gpt)\b", re.I),
]

unflagged_injections = []
for t in threads:
    tid = t["thread_id"]
    pred = v3_preds[tid]
    if "PROMPT_INJECTION" in pred:
        continue
    msg = t["supplier_message"]
    for pat in inj_patterns:
        m = pat.search(msg)
        if m:
            # Check if benign exception
            snippet = msg[max(0, m.start()-25):min(len(msg), m.end()+35)].replace("\n", " ")
            unflagged_injections.append((tid, pat.pattern, m.group(0), snippet, pred))
            break

print(f"Total unflagged potential injection threads: {len(unflagged_injections)}")
for item in unflagged_injections[:30]:
    print(f"[{item[0]}] ({item[2]}): '{item[3]}' -> V3: {item[4]}")
