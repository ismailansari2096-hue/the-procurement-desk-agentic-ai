import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

BASE_DIR = Path(".")
threads = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")

with open("outputs/experimental/submission_v2.csv", "r", encoding="utf-8") as f:
    v2_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

orch = NegotiationOrchestrator(mode="v2")

print("AUDITING GST NOTATIONS ACROSS ALL THREADS...")

old_gst_pat = re.compile(r"(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))", re.I)
new_gst_pat = re.compile(r"(inclusive\s+of\s+GST|including\s+GST|\(?GST\s+included\)?|incl\.?\s+GST)", re.I)

diff_threads = []
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    v2 = v2_preds[tid]
    
    m_old = bool(old_gst_pat.search(latest_msg))
    m_new = bool(new_gst_pat.search(latest_msg))
    
    if m_new != m_old:
        # Check if banned or injection first
        is_inj = "PROMPT_INJECTION" in v2
        is_banned = "BANNED_TERM" in v2
        diff_threads.append((tid, t["category"], t["quantity"], t["round"], v2, latest_msg))

print(f"Total threads with GST regex difference: {len(diff_threads)}")
for item in diff_threads:
    tid, cat, qty, rnd, v2, msg = item
    # Extract line with GST
    for line in msg.split("\n"):
        if "gst" in line.lower():
            print(f"[{tid}] ({cat}, Qty {qty}, Rnd {rnd}) V2={v2} | Line: {line.strip()}")
