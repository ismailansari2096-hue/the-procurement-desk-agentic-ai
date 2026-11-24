import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator
from procurement.banned_terms_detector import BannedTermsDetector
from procurement.thread_parser import ThreadParser

BASE_DIR = Path(".")
threads = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")

with open("outputs/experimental/submission_v2.csv", "r", encoding="utf-8") as f:
    v2_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

orch_v2 = NegotiationOrchestrator(mode="v2")

# Create a clean V3 orchestrator by modifying ThreadParser instance
class RefinedThreadParser(ThreadParser):
    def extract_latest_offer(self, raw_thread, supplier_name, category_id, thread_date, quantity):
        price_inr, parse_err, debug = super().extract_latest_offer(
            raw_thread, supplier_name, category_id, thread_date, quantity
        )
        if price_inr is not None and parse_err is None:
            latest_msg = debug.get("latest_msg", "")
            old_gst = bool(re.search(r"(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))", latest_msg, re.I))
            new_gst = bool(re.search(r"(inclusive\s+of\s+GST|including\s+GST|\(?GST\s+included\)?|incl\.?\s+GST)", latest_msg, re.I))
            if new_gst and not old_gst:
                policy = self.pe.get_effective_policy(category_id, thread_date, supplier_name)
                gst_rate = policy.get("gst_rate", 0.18)
                price_inr = price_inr / (1.0 + gst_rate)
                debug["gst_adjusted_v3"] = True
                debug["effective_inr_price"] = price_inr
        return price_inr, parse_err, debug

# Also refine banned terms detector
class RefinedBannedTermsDetector(BannedTermsDetector):
    def __init__(self):
        super().__init__()
        self.BANNED_EXCLUSIVITY = self.BANNED_EXCLUSIVITY + [
            re.compile(r"buy\s+(these\s+items\s+)?only\s+from\s+us", re.I),
            re.compile(r"purchase\s+only\s+from\s+us", re.I),
        ]

orch_v3 = NegotiationOrchestrator(mode="v2")
orch_v3.thread_agent.parser = RefinedThreadParser(orch_v3.pe)
orch_v3.policy_agent.banned_detector = RefinedBannedTermsDetector()

# Check all threads
diffs = []
for t in threads:
    tid = t["thread_id"]
    v2_val, _ = orch_v2.process_thread(t)
    v3_val, v3_trace = orch_v3.process_thread(t)
    
    if v3_val.label != v2_val.label:
        diffs.append((tid, v2_val.label, v3_val.label, v3_val.fired_step, t))

print(f"Total differences found between V2 and V3: {len(diffs)}")

excl_diffs = [d for d in diffs if "BANNED_TERM" in d[2] and "BANNED_TERM" not in d[1]]
gst_diffs = [d for d in diffs if d not in excl_diffs]

print(f"\n--- EXCLUSIVITY DIFFERENCES ({len(excl_diffs)} threads) ---")
for d in excl_diffs:
    print(f"  {d[0]}: {d[1]} -> {d[2]} (Step {d[3]})")

print(f"\n--- GST DIFFERENCES ({len(gst_diffs)} threads) ---")
for d in gst_diffs:
    print(f"  {d[0]}: {d[1]} -> {d[2]} (Step {d[3]})")
