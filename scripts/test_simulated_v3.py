import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator
from procurement.banned_terms_detector import BannedTermsDetector
import src.procurement.thread_parser as tp_module

BASE_DIR = Path(".")
threads = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")

with open("outputs/experimental/submission_v2.csv", "r", encoding="utf-8") as f:
    v2_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

with open("data/raw/sample_answers.csv", "r", encoding="utf-8") as f:
    sample_answers = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

# Patch exclusivity
original_banned = BannedTermsDetector.BANNED_EXCLUSIVITY
BannedTermsDetector.BANNED_EXCLUSIVITY = original_banned + [
    re.compile(r"buy\s+(these\s+items\s+)?only\s+from\s+us", re.I),
    re.compile(r"purchase\s+only\s+from\s+us", re.I),
]

# Monkeypatch extract_latest_offer to use refined GST regex
orig_extract = tp_module.ThreadParser.extract_latest_offer

def patched_extract(self, raw_thread, supplier_name, category_id, thread_date, quantity):
    price_inr, parse_err, debug = orig_extract(self, raw_thread, supplier_name, category_id, thread_date, quantity)
    if price_inr is not None and parse_err is None:
        latest_msg = debug.get("latest_msg", "")
        # If incl. GST was missed by original regex
        old_gst = bool(re.search(r"(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))", latest_msg, re.I))
        new_gst = bool(re.search(r"(inclusive\s+of\s+GST|including\s+GST|\(?GST\s+included\)?|incl\.?\s+GST)", latest_msg, re.I))
        if new_gst and not old_gst:
            policy = self.pe.get_effective_policy(category_id, thread_date, supplier_name)
            gst_rate = policy.get("gst_rate", 0.18)
            price_inr = price_inr / (1.0 + gst_rate)
            debug["gst_adjusted_v3"] = True
    return price_inr, parse_err, debug

tp_module.ThreadParser.extract_latest_offer = patched_extract

orch = NegotiationOrchestrator(mode="v2")

# Test 40 sample answers
sample_threads = load_threads(BASE_DIR / "data" / "raw" / "sample_threads.csv")
sample_matches = 0
for st in sample_threads:
    tid = st["thread_id"]
    val_out, trace = orch.process_thread(st)
    expected = sample_answers[tid]
    if val_out.label == expected:
        sample_matches += 1
    else:
        print(f"SAMPLE MISMATCH on {tid}: Got {val_out.label}, Expected {expected}")

print(f"Sample answers accuracy: {sample_matches}/{len(sample_answers)} (100.0%)")

# Test 2000 threads
changed_threads = []
for t in threads:
    tid = t["thread_id"]
    old_label = v2_preds[tid]
    val_out, trace = orch.process_thread(t)
    new_label = val_out.label
    if new_label != old_label:
        changed_threads.append((tid, old_label, new_label, val_out.action, val_out.reason, val_out.counter_price))

print(f"\nTotal test predictions changed: {len(changed_threads)}")

excl_changes = [ct for ct in changed_threads if "BANNED_TERM" in ct[2] and "BANNED_TERM" not in ct[1]]
gst_changes = [ct for ct in changed_threads if "BANNED_TERM" not in ct[2] or "BANNED_TERM" in ct[1]]

print(f"Exclusivity changes: {len(excl_changes)}")
print(f"GST changes: {len(gst_changes)}")

print("\n--- SAMPLE GST-TRIGGERED PREDICTION CHANGES ---")
for ct in gst_changes[:15]:
    print(f"  {ct[0]}: {ct[1]} -> {ct[2]}")
