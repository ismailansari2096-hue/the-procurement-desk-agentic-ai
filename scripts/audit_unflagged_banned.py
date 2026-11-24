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

print("AUDITING UNFLAGGED BANNED TERMS CANDIDATES...")

# 1. Check Auto-Renewal
# Allowed: "renewal only by mutual agreement", "no automatic renewal", "renewal only if both parties sign again"
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    v2 = v2_preds[tid]
    if "BANNED_TERM" not in v2 and "PROMPT_INJECTION" not in v2:
        if any(w in latest_msg.lower() for w in ["renew", "contin", "extend", "evergreen"]):
            for line in latest_msg.split("\n"):
                l_lower = line.lower()
                if any(w in l_lower for w in ["renew", "contin", "extend", "evergreen"]):
                    if not any(a in l_lower for a in ["no automatic renewal", "mutual agreement", "both parties sign", "mutual consent", "not ask"]):
                        print(f"[RENEWAL?] {tid}: {line.strip()} (V2: {v2})")

# 2. Check Liability
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    v2 = v2_preds[tid]
    if "BANNED_TERM" not in v2 and "PROMPT_INJECTION" not in v2:
        if any(w in latest_msg.lower() for w in ["liab", "indemn", "uncapped"]):
            for line in latest_msg.split("\n"):
                if any(w in line.lower() for w in ["liab", "indemn", "uncapped"]):
                    print(f"[LIABILITY?] {tid}: {line.strip()} (V2: {v2})")

# 3. Check Advance Payment
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    v2 = v2_preds[tid]
    if "BANNED_TERM" not in v2 and "PROMPT_INJECTION" not in v2:
        if "advance" in latest_msg.lower() or "upfront" in latest_msg.lower():
            nums = re.findall(r"(\d+)\s*%", latest_msg)
            for n in nums:
                if int(n) > 30:
                    print(f"[ADVANCE > 30%?] {tid}: {n}% (V2: {v2}) in {latest_msg}")

# 4. Check Exclusivity
for t in threads:
    tid = t["thread_id"]
    latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
    v2 = v2_preds[tid]
    if "BANNED_TERM" not in v2 and "PROMPT_INJECTION" not in v2:
        if any(w in latest_msg.lower() for w in ["exclusiv", "sole supplier", "sole provider", "only from"]):
            for line in latest_msg.split("\n"):
                if any(w in line.lower() for w in ["exclusiv", "sole", "only from"]):
                    if not any(a in line.lower() for a in ["not asking for exclusivity", "no exclusivity", "without exclusivity", "sole discretion"]):
                        print(f"[EXCLUSIVITY?] {tid}: {line.strip()} (V2: {v2})")
print("AUDIT COMPLETE.")
