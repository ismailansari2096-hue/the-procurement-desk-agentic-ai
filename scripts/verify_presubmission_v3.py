import csv
import hashlib
from pathlib import Path
import sys

BASE_DIR = Path(".")
sys.path.insert(0, str(BASE_DIR / "src"))

from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

v3_path = BASE_DIR / "outputs" / "experimental" / "submission_v3.csv"
v2_path = BASE_DIR / "outputs" / "experimental" / "submission_v2.csv"
v1_path = BASE_DIR / "outputs" / "submission.csv"
threads_path = BASE_DIR / "data" / "raw" / "threads.csv"

# 1 & 2. Read V3
with open(v3_path, "r", encoding="utf-8") as f:
    raw_lines = f.readlines()

header = raw_lines[0].strip()
data_lines = [l.strip() for l in raw_lines[1:] if l.strip()]

check1 = len(data_lines) == 2000
check2 = (header == "thread_id,label")

# 3. Thread IDs check
with open(v3_path, "r", encoding="utf-8") as f:
    v3_rows = list(csv.DictReader(f))

raw_threads = load_threads(threads_path)
expected_tids = [t["thread_id"] for t in raw_threads]
v3_tids = [r["thread_id"] for r in v3_rows]

check3_no_dupes = (len(v3_tids) == len(set(v3_tids)))
check3_match_expected = (v3_tids == expected_tids)
check3 = check3_no_dupes and check3_match_expected

# 4. Label format
valid_actions = {"ACCEPT", "REJECT", "COUNTER", "ESCALATE"}
valid_reasons = {
    "MISSING_INFO", "BLACKLISTED_SUPPLIER", "PROMPT_INJECTION",
    "BANNED_TERM", "ACCEPTABLE_PRICE", "OVER_APPROVAL_LIMIT",
    "ABOVE_WALKAWAY", "COUNTER_OFFER"
}
check4 = True
for r in v3_rows:
    lbl = r["label"]
    parts = lbl.split(":")
    if len(parts) != 3:
        check4 = False
        break
    act, rsn, cp = parts
    if act not in valid_actions or rsn not in valid_reasons:
        check4 = False
        break
    if act == "COUNTER":
        if rsn != "COUNTER_OFFER" or not cp.isdigit() or int(cp) <= 0:
            check4 = False
            break
    else:
        if cp != "":
            check4 = False
            break

# 5. Re-run deterministic pipeline
orch_v3 = NegotiationOrchestrator(mode="v3")
v3_reproduced = True
for i, t in enumerate(raw_threads):
    val_out, _ = orch_v3.process_thread(t)
    if val_out.label != v3_rows[i]["label"]:
        v3_reproduced = False
        break
check5 = v3_reproduced

# 6. Confirm V1 and V2 remain unchanged
def get_sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

v1_sha = get_sha256(v1_path)
v2_sha = get_sha256(v2_path)
v3_sha = get_sha256(v3_path)

AUDITED_V1_SHA = "45f1539a5e466980b4dcea73dc48367b6f9c41196caaef6057fb81881deaa45c"
AUDITED_V2_SHA = "656a98a1f883bcc2a832edc343424b89caa42f70fbad3772eb44d3e8ef774c58"
AUDITED_V3_SHA = "58e741e15a1c3105064bc5b85308c4550148239d9b2752f5eaad5e6783b267ad"

check6 = (v1_sha == AUDITED_V1_SHA and v2_sha == AUDITED_V2_SHA)

# 7. Confirm SHA-256 matches audited V3
check7 = (v3_sha == AUDITED_V3_SHA)

print("=" * 60)
print("FINAL PRE-SUBMISSION VERIFICATION RESULTS")
print("=" * 60)
print(f"Check 1 (Exactly 2,000 data rows):           {'PASS' if check1 else 'FAIL'} ({len(data_lines)} rows)")
print(f"Check 2 (Exact header 'thread_id,label'):    {'PASS' if check2 else 'FAIL'} ('{header}')")
print(f"Check 3 (No duplicate or missing IDs):       {'PASS' if check3 else 'FAIL'} (exact 1:1 match to threads.csv)")
print(f"Check 4 (All labels follow official format): {'PASS' if check4 else 'FAIL'} (all 2,000 valid ACTION:REASON:PRICE)")
print(f"Check 5 (Deterministic pipeline reproduction):{'PASS' if check5 else 'FAIL'} (2,000/2,000 matched)")
print(f"Check 6 (V1 and V2 remain unchanged):        {'PASS' if check6 else 'FAIL'} (SHA-256 verified)")
print(f"Check 7 (SHA-256 matches audited V3 file):   {'PASS' if check7 else 'FAIL'} ({v3_sha})")
print("=" * 60)
