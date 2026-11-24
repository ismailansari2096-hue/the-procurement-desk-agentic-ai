import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import hashlib
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

BASE_DIR = Path(".")
threads = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")
sample_threads = load_threads(BASE_DIR / "data" / "raw" / "sample_threads.csv")

with open(BASE_DIR / "data" / "raw" / "sample_answers.csv", "r", encoding="utf-8") as f:
    sample_answers = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

# 1. Verify 40 worked examples on V2 and V3
print("=== 1. VERIFYING 40 WORKED EXAMPLES ===")
for mode in ["v1", "v2", "v3"]:
    orch = NegotiationOrchestrator(mode=mode)
    matches = 0
    for st in sample_threads:
        tid = st["thread_id"]
        val_out, _ = orch.process_thread(st)
        if val_out.label == sample_answers[tid]:
            matches += 1
    print(f"Mode {mode.upper()}: {matches}/40 worked examples matched ({matches/40*100:.1f}%)")
    assert matches == 40, f"Mode {mode} failed worked examples!"

# 2. Verify V1 Reproduction
print("\n=== 2. VERIFYING V1 REPRODUCTION AGAINST outputs/submission.csv ===")
with open("outputs/submission.csv", "r", encoding="utf-8") as f:
    v1_rows = list(csv.DictReader(f))
v1_expected = {r["thread_id"]: r["label"] for r in v1_rows}

orch_v1 = NegotiationOrchestrator(mode="v1")
v1_matches = 0
for t in threads:
    tid = t["thread_id"]
    val_out, _ = orch_v1.process_thread(t)
    if val_out.label == v1_expected[tid]:
        v1_matches += 1

print(f"V1 exact matches: {v1_matches}/2000 ({v1_matches/2000*100:.2f}%)")
assert v1_matches == 2000, "V1 reproduction mismatch!"

# 3. Verify V2 Reproduction
print("\n=== 3. VERIFYING V2 REPRODUCTION AGAINST outputs/experimental/submission_v2.csv ===")
with open("outputs/experimental/submission_v2.csv", "r", encoding="utf-8") as f:
    v2_rows = list(csv.DictReader(f))
v2_expected = {r["thread_id"]: r["label"] for r in v2_rows}

orch_v2 = NegotiationOrchestrator(mode="v2")
v2_matches = 0
for t in threads:
    tid = t["thread_id"]
    val_out, _ = orch_v2.process_thread(t)
    if val_out.label == v2_expected[tid]:
        v2_matches += 1

print(f"V2 exact matches: {v2_matches}/2000 ({v2_matches/2000*100:.2f}%)")
assert v2_matches == 2000, "V2 reproduction mismatch!"

# 4. Generate V3 Predictions
print("\n=== 4. GENERATING V3 PREDICTIONS ===")
orch_v3 = NegotiationOrchestrator(mode="v3")
v3_predictions = []
diff_from_v2 = []

for t in threads:
    tid = t["thread_id"]
    val_out, trace = orch_v3.process_thread(t)
    v3_predictions.append({"thread_id": tid, "label": val_out.label})
    if val_out.label != v2_expected[tid]:
        diff_from_v2.append({
            "thread_id": tid,
            "category": t["category"],
            "supplier": t["supplier"],
            "quantity": t["quantity"],
            "round": t["round"],
            "v2_label": v2_expected[tid],
            "v3_label": val_out.label,
            "fired_step": val_out.fired_step,
            "reason": val_out.reason
        })

print(f"Total V3 predictions generated: {len(v3_predictions)}")
print(f"Total differences between V2 and V3: {len(diff_from_v2)}")

out_v3_path = BASE_DIR / "outputs" / "experimental" / "submission_v3.csv"
with open(out_v3_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["thread_id", "label"])
    writer.writeheader()
    writer.writerows(v3_predictions)

# Compute SHA-256
with open(out_v3_path, "rb") as f:
    v3_sha = hashlib.sha256(f.read()).hexdigest()

print(f"V3 file saved to: {out_v3_path}")
print(f"V3 SHA-256: {v3_sha}")
