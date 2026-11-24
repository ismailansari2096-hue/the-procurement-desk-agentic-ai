import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

sample_threads = load_threads(Path("data/raw/sample_threads.csv"))
with open("data/raw/sample_answers.csv", "r", encoding="utf-8") as f:
    sample_answers = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

orch = NegotiationOrchestrator(mode="v3")

for st in sample_threads:
    tid = st["thread_id"]
    ans = sample_answers[tid]
    cat = st["category"]
    if cat in ["cloud-servers", "crm-licenses", "design-software"]:
        val_out, trace = orch.process_thread(st)
        print(f"[{tid}] ({cat}) -> Expected: {ans} | Got: {val_out.label}")
        tu = trace["thread_understanding"]
        pol = trace["policy_compliance"]
        print(f"  Qty: {st['quantity']} | Unit price INR: {tu.effective_inr_price} | Approval limit: {pol.effective_approval_limit}")
        print(f"  Deal val: {tu.effective_inr_price * int(st['quantity'])} vs Approval: {pol.effective_approval_limit}")
