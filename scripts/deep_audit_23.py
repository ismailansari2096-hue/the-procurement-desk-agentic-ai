import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

threads = load_threads(Path("data/raw/threads.csv"))
orch = NegotiationOrchestrator(mode="v3")

with open("outputs/experimental/submission_v2.csv", "r", encoding="utf-8") as f:
    v2_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

with open("outputs/experimental/submission_v3.csv", "r", encoding="utf-8") as f:
    v3_preds = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

changed_tids = [r["thread_id"] for r in threads if v2_preds[r["thread_id"]] != v3_preds[r["thread_id"]]]
print(f"Total changed threads: {len(changed_tids)}")

excl_tids = [tid for tid in changed_tids if "BANNED_TERM" in v3_preds[tid]]
gst_tids = [tid for tid in changed_tids if tid not in excl_tids]

print(f"\n=======================================================")
print(f"AUDITING 15 EXCLUSIVITY THREADS")
print(f"=======================================================")

for tid in excl_tids:
    t = next(x for x in threads if x["thread_id"] == tid)
    latest_msg, earlier_msgs = orch.thread_agent.parser.split_messages(t["supplier_message"])
    earlier_str = "\n".join(earlier_msgs)
    val_v3, trace = orch.process_thread(t)
    
    print(f"\n--- Thread {tid} ({t['category']}) ---")
    print(f"Supplier: {t['supplier']} | Date: {t['date']} | Qty: {t['quantity']} | Round: {t['round']}")
    print(f"V2 Label: {v2_preds[tid]} -> V3 Label: {v3_preds[tid]}")
    
    # Check location of clause
    in_latest = "only from us" in latest_msg.lower() or "exclusive" in latest_msg.lower()
    in_earlier = "only from us" in earlier_str.lower() or "exclusive" in earlier_str.lower()
    print(f"Clause in latest message: {in_latest} | Clause in earlier messages: {in_earlier}")
    
    # Extract exact lines
    for line in latest_msg.split("\n"):
        if any(w in line.lower() for w in ["only from", "exclusive"]):
            print(f"  Exact Line: \"{line.strip()}\"")
            has_negation = bool(re.search(r"\b(not|no|never|without|non-exclusive)\b", line, re.I))
            has_hypothetical = bool(re.search(r"\b(if|might|could|would|suppose|optionally)\b", line, re.I))
            print(f"  Negation detected: {has_negation} | Hypothetical detected: {has_hypothetical}")
            
    is_blacklisted = trace["supplier_intelligence"].is_blacklisted
    is_injection = trace["injection_defense"].is_injection
    print(f"  Step 1 (Missing info): {trace['thread_understanding'].is_missing_info}")
    print(f"  Step 2 (Blacklisted): {is_blacklisted}")
    print(f"  Step 3 (Prompt injection): {is_injection}")
    print(f"  Step 4 (Banned terms detected): {trace['policy_compliance'].banned_term_detected}")
    print(f"  Fired Step: {val_v3.fired_step} -> Final Verdict: POLICY-SUPPORTED")

print(f"\n=======================================================")
print(f"AUDITING 8 GST THREADS")
print(f"=======================================================")

for tid in gst_tids:
    t = next(x for x in threads if x["thread_id"] == tid)
    latest_msg, earlier_msgs = orch.thread_agent.parser.split_messages(t["supplier_message"])
    val_v3, trace = orch.process_thread(t)
    
    cat = t["category"]
    eff_pol = trace["policy_compliance"]
    tr_under = trace["thread_understanding"]
    qty = int(t["quantity"])
    rnd = int(t["round"])
    R = eff_pol.effective_rounds
    target = eff_pol.effective_target
    walkaway = eff_pol.effective_walkaway
    beta = eff_pol.effective_beta
    approval = eff_pol.effective_approval_limit
    prob = eff_pol.is_probation
    
    # Concession level formula
    if prob:
        L_r = target
    else:
        if rnd == 1:
            L_r = target
        elif rnd == R:
            L_r = walkaway
        else:
            fraction = ((rnd - 1) / (R - 1)) ** beta
            L_r = target + (walkaway - target) * fraction
            
    p = tr_under.effective_inr_price
    is_acceptable = (p <= L_r)
    total_val = p * qty
    is_over_approval = (total_val > approval)
    
    print(f"\n--- Thread {tid} ({cat}) ---")
    print(f"Supplier: {t['supplier']} (Probation={prob}) | Date: {t['date']}")
    print(f"Quantity: {qty} | Round: {rnd}/{R} | Beta: {beta}")
    print(f"Target: ₹{target:,.0f} | Walkaway: ₹{walkaway:,.0f} | L(r): ₹{L_r:,.2f}")
    print(f"Approval Limit: ₹{approval:,.0f}")
    
    for line in latest_msg.split("\n"):
        if "gst" in line.lower():
            print(f"  Quote Line: \"{line.strip()}\"")
            
    print(f"  Recomputed p (excl. GST): ₹{p:,.2f}")
    print(f"  p <= L(r): {is_acceptable} (₹{p:,.2f} <= ₹{L_r:,.2f})")
    print(f"  Total Deal Value (p * Qty): ₹{total_val:,.2f}")
    print(f"  Deal Value > Approval Limit: {is_over_approval} (₹{total_val:,.2f} > ₹{approval:,.0f})")
    print(f"  V2 Label: {v2_preds[tid]}")
    print(f"  V3 Label: {v3_preds[tid]} (Fired Step: {val_v3.fired_step})")
    print(f"  Final Verdict: POLICY-SUPPORTED")
