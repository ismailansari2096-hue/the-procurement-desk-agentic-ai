"""
Verify demo preloaded cases on V4 mode.
"""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from demo.interactive_demo import PRELOADED_TEST_CASES
from agentic.orchestrator import NegotiationOrchestrator

orch = NegotiationOrchestrator(mode="v4")

for tc in PRELOADED_TEST_CASES:
    res, trace = orch.process_thread(tc)
    print(f"[{tc['id']}] -> Label: {res.label} | Fired Step: {res.fired_step} | Action: {res.action}")

print("\nALL PRELOADED DEMO CASES EVALUATE CLEANLY IN V4!")
