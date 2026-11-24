"""
Phase 2 Final Verification Checks.
"""

import subprocess
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from demo.interactive_demo import PRELOADED_TEST_CASES
from agentic.orchestrator import NegotiationOrchestrator

def main():
    print("=" * 65)
    print("PHASE 2 — RUN FINAL CHECKS")
    print("=" * 65)

    # 1. Run pytest -v
    print("\n[CHECK 1] Running pytest -v...")
    res = subprocess.run([sys.executable, "-m", "pytest", "-v"], capture_output=True, text=True)
    summary_line = [l for l in res.stdout.splitlines() if "passed" in l][-1]
    print(f"  Pytest Result: {summary_line.strip()}")
    assert res.returncode == 0, f"Pytest failed:\n{res.stdout}"

    # 2 & 3. Run all five interactive demo scenarios in V4 mode
    print("\n[CHECK 2 & 3] Running 5 Demo Scenarios on V4 Engine...")
    orch = NegotiationOrchestrator(mode="v4")
    expected_labels = [
        ("CASE-1-COUNTER", "COUNTER:COUNTER_OFFER:96000"),
        ("CASE-2-VOLUME-DISCOUNT", "ACCEPT:ACCEPTABLE_PRICE:"),
        ("CASE-3-PROMPT-INJECTION", "ESCALATE:PROMPT_INJECTION:"),
        ("CASE-4-BANNED-TERM", "ESCALATE:BANNED_TERM:"),
        ("CASE-5-OVER-APPROVAL", "ESCALATE:OVER_APPROVAL_LIMIT:")
    ]

    for idx, (tc, (exp_id, exp_lbl)) in enumerate(zip(PRELOADED_TEST_CASES, expected_labels), 1):
        assert tc["id"] == exp_id
        dec, trace = orch.process_thread(tc)
        print(f"  Scenario {idx} [{tc['id']}]: {dec.label}")
        assert dec.label == exp_lbl, f"Mismatch on {tc['id']}: got {dec.label}, expected {exp_lbl}"

    print("  All 5 scenarios match expected output labels exactly!")

    # 4. Verify dashboard header and labels
    print("\n[CHECK 4] Verifying demo/index.html UI labels...")
    html = open(root_dir / "demo" / "index.html", encoding="utf-8").read()
    assert "V4 Model • Kaggle Public Score: 1.00000" in html, "Missing V4 public score badge"
    assert "Public Leaderboard Score — Private Score Pending" in html, "Missing pending private score label"
    print("  Header Badge : 'V4 Model • Kaggle Public Score: 1.00000' -> PRESENT")
    print("  Disclosure   : 'Public Leaderboard Score — Private Score Pending' -> PRESENT")

    print("\n" + "=" * 65)
    print("PHASE 2 CHECKS: ALL PASS")
    print("=" * 65)

if __name__ == "__main__":
    main()
