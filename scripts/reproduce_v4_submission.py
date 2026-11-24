"""
Exact Final Kaggle Submission (V4) Reproducibility Script.
Competition: Data Sprint 2.0 (Agentic AI Track)
Project: The Procurement Desk — Agentic AI Decision Engine
Team: Beyond limits

This script runs the deterministic V4 NegotiationOrchestrator over data/raw/threads.csv
and generates the exact competition submission file, asserting a byte-for-byte match
with the verified reference SHA-256 hash:
a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92
"""

import sys
import csv
import hashlib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

from agentic.orchestrator import NegotiationOrchestrator

EXPECTED_SHA256 = "a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92"


def reproduce_v4_submission(
    input_csv: Path = ROOT_DIR / "data" / "raw" / "threads.csv",
    output_csv: Path = ROOT_DIR / "submission_v4.csv",
    reference_csv: Path = ROOT_DIR / "outputs" / "experimental" / "submission_v4.csv"
) -> bool:
    print("=" * 70)
    print("REPRODUCING FINAL V4 KAGGLE SUBMISSION")
    print(f"Target SHA-256: {EXPECTED_SHA256}")
    print("=" * 70)

    if not input_csv.exists():
        print(f"[-] ERROR: Input threads file not found at: {input_csv}")
        return False

    print(f"[*] Reading input threads from: {input_csv}")
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        threads = list(reader)

    print(f"[+] Loaded {len(threads)} threads.")
    assert len(threads) == 2000, f"Expected 2000 threads, got {len(threads)}"

    print("[*] Initializing NegotiationOrchestrator(mode='v4')...")
    orchestrator = NegotiationOrchestrator(mode="v4")

    results = []
    print("[*] Processing threads through 6-Agent pipeline...")
    for idx, thread in enumerate(threads, 1):
        decision_out, _ = orchestrator.process_thread(thread)
        results.append((thread["thread_id"], decision_out.label))
        if idx % 500 == 0 or idx == len(threads):
            print(f"    Processed {idx}/{len(threads)} threads...")

    print(f"[*] Writing reproduced predictions to: {output_csv}")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerow(["thread_id", "label"])
        for tid, lbl in results:
            writer.writerow([tid, lbl])

    reproduced_bytes = output_csv.read_bytes()
    reproduced_hash = hashlib.sha256(reproduced_bytes).hexdigest()
    print(f"[+] Reproduced File SHA-256: {reproduced_hash}")

    hash_match = (reproduced_hash == EXPECTED_SHA256)
    byte_match = False

    if reference_csv.exists():
        ref_bytes = reference_csv.read_bytes()
        ref_hash = hashlib.sha256(ref_bytes).hexdigest()
        byte_match = (reproduced_bytes == ref_bytes)
        print(f"[+] Reference File SHA-256 : {ref_hash}")
        print(f"[+] Byte-for-byte exact match: {byte_match}")

    print("=" * 70)
    if hash_match and (not reference_csv.exists() or byte_match):
        print("[PASS] EXACT REPRODUCIBILITY VERIFIED (100% BIT-FOR-BIT MATCH)!")
        print("=" * 70)
        return True
    else:
        print("[FAIL] HASH OR BYTE MISMATCH DETECTED!")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = reproduce_v4_submission()
    sys.exit(0 if success else 1)
