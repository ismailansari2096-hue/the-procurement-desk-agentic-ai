import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

threads = load_threads(Path("data/raw/threads.csv"))
t10290 = next(t for t in threads if t["thread_id"] == "T10290")

orch = NegotiationOrchestrator(mode="v2")

# Run without patch
out_v2, trace_v2 = orch.process_thread(t10290)
print(f"V2 Decision: {out_v2.label}")
print(f"V2 Effective INR price: {trace_v2['thread_understanding'].effective_inr_price}")
print(f"V2 Effective Walkaway: {trace_v2['policy_compliance'].effective_walkaway}")
print(f"V2 Effective Target: {trace_v2['policy_compliance'].effective_target}")
print(f"V2 Effective Approval Limit: {trace_v2['policy_compliance'].effective_approval_limit}")
price_excl_gst = 95813.0 / 1.18
qty = 300
total_val = price_excl_gst * qty
approval = trace_v2['policy_compliance'].effective_approval_limit
print(f"Price excl GST: {price_excl_gst:.2f}")
print(f"Total deal value: {total_val:.2f} vs Approval Limit: {approval:.2f}")
if total_val > approval:
    print("Deal value > approval limit -> ESCALATE:OVER_APPROVAL_LIMIT:")
else:
    print("Deal value <= approval limit -> ACCEPT:ACCEPTABLE_PRICE:")
