"""
Comprehensive verification of all 5 preloaded test cases on V4 production orchestrator.
"""

import sys
import json
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from demo.interactive_demo import PRELOADED_TEST_CASES
from agentic.orchestrator import NegotiationOrchestrator

def main():
    print("=" * 65)
    print("VERIFYING DEMO TEST CASES AGAINST PRODUCTION V4 ORCHESTRATOR")
    print("=" * 65)

    orch = NegotiationOrchestrator(mode="v4")
    assert orch.mode == "v4", "Orchestrator must be in V4 mode"
    assert orch.thread_agent.enable_v4_word_pricing is True, "V4 word pricing must be active"
    assert orch.thread_agent.enable_v3_gst is True, "V3 GST normalization must be active"
    assert orch.policy_agent.enable_v3_exclusivity is True, "V3 exclusivity filter must be active"

    expected_results = [
        {
            "id": "CASE-1-COUNTER",
            "expected_action": "COUNTER",
            "expected_reason": "COUNTER_OFFER",
            "expected_counter": "96000",
            "expected_step": 5,
            "expected_label": "COUNTER:COUNTER_OFFER:96000"
        },
        {
            "id": "CASE-2-VOLUME-DISCOUNT",
            "expected_action": "ACCEPT",
            "expected_reason": "ACCEPTABLE_PRICE",
            "expected_counter": "",
            "expected_step": 6,
            "expected_label": "ACCEPT:ACCEPTABLE_PRICE:"
        },
        {
            "id": "CASE-3-PROMPT-INJECTION",
            "expected_action": "ESCALATE",
            "expected_reason": "PROMPT_INJECTION",
            "expected_counter": "",
            "expected_step": 3,
            "expected_label": "ESCALATE:PROMPT_INJECTION:"
        },
        {
            "id": "CASE-4-BANNED-TERM",
            "expected_action": "ESCALATE",
            "expected_reason": "BANNED_TERM",
            "expected_counter": "",
            "expected_step": 4,
            "expected_label": "ESCALATE:BANNED_TERM:"
        },
        {
            "id": "CASE-5-OVER-APPROVAL",
            "expected_action": "ESCALATE",
            "expected_reason": "OVER_APPROVAL_LIMIT",
            "expected_counter": "",
            "expected_step": 6,
            "expected_label": "ESCALATE:OVER_APPROVAL_LIMIT:"
        }
    ]

    for idx, (tc, exp) in enumerate(zip(PRELOADED_TEST_CASES, expected_results), 1):
        assert tc["id"] == exp["id"], f"Case ID mismatch at {idx}"
        dec_out, trace = orch.process_thread(tc)

        print(f"\n[Case {idx}: {tc['title']}]")
        print(f"  Thread ID     : {tc['thread_id']}")
        print(f"  Supplier      : {tc['supplier']} | Category: {tc['category']} | Round: {tc['round']} | Qty: {tc['quantity']}")
        print(f"  Engine Mode   : {trace['mode']}")
        print(f"  Decision Label: {dec_out.label}")
        print(f"  Fired Step    : Step {dec_out.fired_step}")
        print(f"  Action/Reason : {dec_out.action} / {dec_out.reason}")
        if dec_out.counter_price:
            print(f"  Counter Price : INR {dec_out.counter_price}")

        # Assertions
        assert dec_out.label == exp["expected_label"], f"Mismatch on {tc['id']}: got {dec_out.label}, expected {exp['expected_label']}"
        assert dec_out.action == exp["expected_action"], f"Action mismatch on {tc['id']}"
        assert dec_out.reason == exp["expected_reason"], f"Reason mismatch on {tc['id']}"
        assert dec_out.counter_price == exp["expected_counter"], f"Counter price mismatch on {tc['id']}"
        assert dec_out.fired_step == exp["expected_step"], f"Step mismatch on {tc['id']}"
        print(f"  Status        : PASS (100% Match)")

    print("\n" + "=" * 65)
    print("ALL 5 PRELOADED DEMO CASES FULLY VERIFIED ON ACTUAL V4 ENGINE!")
    print("=" * 65)

if __name__ == "__main__":
    main()
