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

vol_existing_regex = re.compile(
    r"with\s+a\s+further\s+(\d+)\s*%\s*off\s+for\s+orders\s+of\s+(\d+)\s+([a-zA-Z\s]+?)\s+or\s+more",
    re.I
)
prev_quote_regex = re.compile(
    r"(\d+)\s*%\s*(?:discount\s+on|off)\s+our\s+previous\s+quote",
    re.I
)
list_price_regex = re.compile(
    r"(\d+)\s*%\s*discount\s+on\s+our\s+list\s+price\s+of\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)",
    re.I
)

remainder = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    if not vol_existing_regex.search(latest_msg) and not prev_quote_regex.search(latest_msg) and not list_price_regex.search(latest_msg):
        if re.search(r"\b(discount|%\s*off)\b", latest_msg, re.I):
            remainder.append((tid, latest_msg))

print(f"Total leftover discount threads: {len(remainder)}")
for tid, msg in remainder[:20]:
    for line in msg.split("\n"):
        if re.search(r"\b(discount|%\s*off)\b", line, re.I):
            print(f"[{tid}]: {line.strip()}")
