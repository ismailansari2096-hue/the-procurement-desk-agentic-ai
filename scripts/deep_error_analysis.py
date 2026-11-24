"""
Deep Error Analysis Script for 2,000 Threads.
Audits threads.csv against all playbook rules, precedents, and edge cases.
"""

import sys
import re
import csv
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from procurement.data_loader import load_threads
from agentic.orchestrator import NegotiationOrchestrator

THREADS = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")
V2_CSV = BASE_DIR / "outputs" / "experimental" / "submission_v2.csv"

with open(V2_CSV, "r", encoding="utf-8") as f:
    V2_ROWS = list(csv.DictReader(f))

V2_PREDS = {r["thread_id"]: r["label"] for r in V2_ROWS}


def scan_prompt_injections():
    print("\n--- 1. AUDITING PROMPT INJECTIONS & ADVERSARIAL PATTERNS ---")
    suspicious_patterns = [
        ("NON_ASCII / MULTILINGUAL", re.compile(r"[^\x00-\x7F]")),
        ("PROMPT_WORD", re.compile(r"\b(prompt|jailbreak|injection|bypass|override)\b", re.I)),
        ("INSTRUCTION_TARGET", re.compile(r"\b(instructions?\s+for|directives?\s+for|rules?\s+for)\b", re.I)),
        ("SYSTEM_WORD", re.compile(r"\b(system\s+note|system\s+message|system\s+directive|system\s+admin)\b", re.I)),
        ("EXECUTIVE_CLAIM", re.compile(r"\b(cfo|ceo|coo|cto|vp|director|board)\b", re.I)),
        ("BOT_WORD", re.compile(r"\b(bot|crawler|automaton|automated\s+agent|ai\s+agent)\b", re.I)),
        ("PREAPPROVED", re.compile(r"\b(pre[- ]approved|already\s+approved|prior\s+approval)\b", re.I)),
        ("CONFIRM_NOW", re.compile(r"\b(accept\s+now|confirm\s+immediately|approve\s+this\s+deal)\b", re.I)),
    ]

    orch = NegotiationOrchestrator(mode="v2")
    non_inj_flagged = []

    for t in THREADS:
        tid = t["thread_id"]
        v2_label = V2_PREDS[tid]
        msg = t["supplier_message"]

        # If not already ESCALATE:PROMPT_INJECTION
        if "PROMPT_INJECTION" not in v2_label:
            for name, pat in suspicious_patterns:
                m = pat.search(msg)
                if m:
                    # Check if it looks adversarial
                    snippet = msg[max(0, m.start()-30):min(len(msg), m.end()+50)].replace("\n", " ")
                    non_inj_flagged.append((tid, name, m.group(0), snippet, v2_label))
                    break

    print(f"Total non-injection threads matching suspicious patterns: {len(non_inj_flagged)}")
    # Print sample
    for item in non_inj_flagged[:20]:
        print(f"  [{item[0]}] ({item[1]} -> '{item[2]}'): '{item[3]}' [V2: {item[4]}]")

    return non_inj_flagged


def scan_banned_terms():
    print("\n--- 2. AUDITING BANNED CONTRACT TERMS ---")
    patterns = [
        ("ADVANCE_WORD", re.compile(r"\b(upfront|advance|deposit|retainer|down\s*payment)\b", re.I)),
        ("RENEWAL_WORD", re.compile(r"\b(renew|renewal|continues|extends|successive|evergreen)\b", re.I)),
        ("LIABILITY_WORD", re.compile(r"\b(liability|indemnif|harmless|damages|uncapped)\b", re.I)),
        ("EXCLUSIVITY_WORD", re.compile(r"\b(exclusive|exclusivity|sole|solely|only\s+from)\b", re.I)),
    ]

    orch = NegotiationOrchestrator(mode="v2")
    banned_candidates = []

    for t in THREADS:
        tid = t["thread_id"]
        v2_label = V2_PREDS[tid]
        latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])

        if "BANNED_TERM" not in v2_label and "PROMPT_INJECTION" not in v2_label:
            for name, pat in patterns:
                m = pat.search(latest_msg)
                if m:
                    snippet = latest_msg[max(0, m.start()-30):min(len(latest_msg), m.end()+50)].replace("\n", " ")
                    banned_candidates.append((tid, name, m.group(0), snippet, v2_label))
                    break

    print(f"Total non-banned threads matching term patterns in latest msg: {len(banned_candidates)}")
    for item in banned_candidates[:25]:
        print(f"  [{item[0]}] ({item[1]} -> '{item[2]}'): '{item[3]}' [V2: {item[4]}]")

    return banned_candidates


def scan_missing_info():
    print("\n--- 3. AUDITING MISSING_INFO THREADS ---")
    missing_threads = [t for t in THREADS if V2_PREDS[t["thread_id"]] == "ESCALATE:MISSING_INFO:"]
    print(f"Total MISSING_INFO threads in V2: {len(missing_threads)}")

    orch = NegotiationOrchestrator(mode="v2")
    for t in missing_threads[:20]:
        tid = t["thread_id"]
        latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])
        print(f"\n--- Thread {tid} ({t['category']}) Qty: {t['quantity']} Round: {t['round']} ---")
        print(f"Latest Msg:\n{latest_msg.strip()[:200]}")


def scan_volume_discounts_and_concessions():
    print("\n--- 4. AUDITING VOLUME DISCOUNTS & UNUSUAL CONCESSIONS ---")
    vol_patterns = [
        re.compile(r"(\d+)\s*%\s*(?:off|discount)\s+for\s+orders", re.I),
        re.compile(r"volume\s+discount", re.I),
        re.compile(r"bulk\s+discount", re.I),
        re.compile(r"orders\s+of\s+\d+\s+or\s+more", re.I),
        re.compile(r"plus\s+\d+\s+free", re.I),
        re.compile(r"free\s+\w+\s+for\s+every", re.I),
        re.compile(r"buy\s+\d+\s+get", re.I),
        re.compile(r"per\s+dozen", re.I),
        re.compile(r"per\s+pack", re.I),
        re.compile(r"per\s+box", re.I),
        re.compile(r"per\s+ream", re.I),
    ]

    orch = NegotiationOrchestrator(mode="v2")
    matches = []
    for t in THREADS:
        tid = t["thread_id"]
        v2_label = V2_PREDS[tid]
        latest_msg, _ = orch.thread_agent.parser.split_messages(t["supplier_message"])

        for pat in vol_patterns:
            m = pat.search(latest_msg)
            if m:
                snippet = latest_msg[max(0, m.start()-20):min(len(latest_msg), m.end()+40)].replace("\n", " ")
                matches.append((tid, pat.pattern, m.group(0), snippet, t['quantity'], v2_label))
                break

    print(f"Total threads matching discount/concession patterns: {len(matches)}")
    for item in matches[:30]:
        print(f"  [{item[0]}] Qty {item[4]} ('{item[2]}'): '{item[3]}' -> V2: {item[5]}")


if __name__ == "__main__":
    scan_prompt_injections()
    scan_banned_terms()
    scan_missing_info()
    scan_volume_discounts_and_concessions()
