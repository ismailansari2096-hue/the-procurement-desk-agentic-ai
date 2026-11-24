"""
Re-generation and validation script for experimental V4 candidate.
Fixes:
- Bug in words-to-numbers price extraction: word_tokens regex prefix ordering
  where single-digit prefix tokens ('six', 'seven', 'eight', 'nine') shadowed
  compound decade and teen numbers ('sixteen', 'seventeen', 'sixty', 'seventy', etc.),
  causing prices like 'seventy-one thousand seven hundred' to be parsed as 7.0 rupees.
Official Policy Reference:
- units-and-currency.md: 'Notation: amounts may be written in words.'
- decision-procedure.md: 'Step 5. Price decision. Normalize the supplier's current offer to p.'
"""

import sys
import csv
import hashlib
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from agentic.orchestrator import NegotiationOrchestrator


def main():
    print("=" * 65)
    print("BUILDING AND VALIDATING EXPERIMENTAL V4 CANDIDATE")
    print("=" * 65)

    raw_threads_path = root_dir / "data" / "raw" / "threads.csv"
    with open(raw_threads_path, "r", encoding="utf-8") as f:
        threads = list(csv.DictReader(f))

    # 1. Verify V3 benchmark
    orch_v3 = NegotiationOrchestrator(mode="v3")
    v3_path = root_dir / "outputs" / "experimental" / "submission_v3.csv"
    with open(v3_path, "r", encoding="utf-8") as f:
        v3_rows = list(csv.DictReader(f))
    v3_dict = {r["thread_id"]: r["label"] for r in v3_rows}

    # 2. Run V4 Orchestrator
    orch_v4 = NegotiationOrchestrator(mode="v4")
    v4_results = []
    diffs = []

    for t in threads:
        tid = t["thread_id"]
        v3_label = v3_dict[tid]
        v4_out, trace_v4 = orch_v4.process_thread(t)
        v4_label = v4_out.label
        v4_results.append((tid, v4_label))

        if v4_label != v3_label:
            p_v3 = trace_v4["thread_understanding"].debug_details.get("extracted_price")
            p_v4 = trace_v4["thread_understanding"].effective_inr_price
            diffs.append({
                "thread_id": tid,
                "category": t["category"],
                "supplier": t["supplier"],
                "round": t["round"],
                "quantity": t["quantity"],
                "v3_label": v3_label,
                "v4_label": v4_label,
                "p_v4": p_v4,
                "message": t["supplier_message"].replace("\n", " ")
            })

    # Save V4 to outputs/experimental/submission_v4.csv
    v4_out_path = root_dir / "outputs" / "experimental" / "submission_v4.csv"
    v4_out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(v4_out_path, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerow(["thread_id", "label"])
        for tid, lbl in v4_results:
            writer.writerow([tid, lbl])

    # Compute SHA-256
    v4_hash = hashlib.sha256(open(v4_out_path, "rb").read()).hexdigest()

    print(f"Total Threads Evaluated : {len(v4_results)}")
    print(f"Total Changes (V3 -> V4): {len(diffs)} / 2000 ({len(diffs)/20:.2f}%)")
    print(f"V4 File Path            : {v4_out_path}")
    print(f"V4 SHA-256              : {v4_hash}")
    print("=" * 65)

    print("\nALL 33 CHANGED THREADS DETAILED:")
    for idx, d in enumerate(diffs, 1):
        print(f"[{idx:02d}] {d['thread_id']} ({d['category']}, {d['supplier']}, Rnd {d['round']}, Qty {d['quantity']}):")
        print(f"     V3: {d['v3_label']}  -->  V4: {d['v4_label']} (Effective Price: INR {d['p_v4']:.2f})")
        print(f"     Msg excerpt: {d['message'][-140:]}")
        print("-" * 65)

    # Save verification report
    report_path = root_dir / "reports" / "v4_diff_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# V3 vs V4 Differential Verification Report\n\n")
        f.write(f"- **V4 Path:** `{v4_out_path}`\n")
        f.write(f"- **V4 SHA-256:** `{v4_hash}`\n")
        f.write(f"- **Total Changes:** {len(diffs)} / 2000\n\n")
        f.write("| # | Thread ID | Category | Supplier | Round | Qty | V3 Label | V4 Label | Effective Price |\n")
        f.write("|---|---|---|---|:---:|:---:|---|---|---:|\n")
        for idx, d in enumerate(diffs, 1):
            f.write(f"| {idx} | {d['thread_id']} | {d['category']} | {d['supplier']} | {d['round']} | {d['quantity']} | `{d['v3_label']}` | `{d['v4_label']}` | ₹{d['p_v4']:.2f} |\n")

    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
