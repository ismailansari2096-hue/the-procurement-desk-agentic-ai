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

other_discounts = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    if not vol_existing_regex.search(latest_msg):
        for line in latest_msg.split("\n"):
            line_str = line.strip()
            # check if line has discount or off
            if re.search(r"\b(\d+%\s*off|\d+%\s*discount|volume\s+discount|bulk\s+discount)\b", line_str, re.I):
                other_discounts.append((tid, line_str))

print(f"Total lines with discount not matching VOL_EXISTING: {len(other_discounts)}")
for tid, line in other_discounts[:30]:
    print(f"[{tid}]: {line}")
