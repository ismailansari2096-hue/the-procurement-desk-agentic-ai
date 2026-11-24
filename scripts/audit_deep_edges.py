"""
Comprehensive Deep Audit Script.
Scans all 2,000 threads for edge cases across Banned Terms, Prompt Injections,
Free Units, Volume Discounts, Pack Conversions, and GST.
"""

import sys
import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from procurement.data_loader import load_threads

THREADS = load_threads(BASE_DIR / "data" / "raw" / "threads.csv")
V2_CSV = BASE_DIR / "outputs" / "experimental" / "submission_v2.csv"

with open(V2_CSV, "r", encoding="utf-8") as f:
    V2_ROWS = list(csv.DictReader(f))

V2_PREDS = {r["thread_id"]: r["label"] for r in V2_ROWS}


def split_latest(msg):
    return msg.split("[Earlier message")[0]


def audit_exclusivity():
    print("=" * 70)
    print("1. AUDITING MISSED EXCLUSIVITY CLAUSES")
    print("=" * 70)
    pats = [
        re.compile(r"buy\s+.*?only\s+from\s+us", re.I),
        re.compile(r"purchase\s+.*?only\s+from\s+us", re.I),
        re.compile(r"source\s+.*?only\s+from\s+us", re.I),
        re.compile(r"buy\s+only\s+from\s+us", re.I),
        re.compile(r"exclusive\s+(supplier|vendor|provider|partner|dealer|distributor)", re.I),
        re.compile(r"sole\s+(supplier|vendor|provider|partner|source)", re.I),
        re.compile(r"exclusivity", re.I)
    ]
    missed = []
    for t in THREADS:
        tid = t["thread_id"]
        latest = split_latest(t["supplier_message"])
        if re.search(r"not\s+asking\s+for\s+exclusivity|no\s+exclusivity\s+is\s+asked|without\s+exclusivity", latest, re.I):
            continue
        for p in pats:
            m = p.search(latest)
            if m:
                if "BANNED_TERM" not in V2_PREDS[tid] and "PROMPT_INJECTION" not in V2_PREDS[tid]:
                    snippet = latest[max(0, m.start()-30):min(len(latest), m.end()+40)].replace("\n", " ")
                    missed.append((tid, m.group(0), snippet, V2_PREDS[tid]))
                break

    print(f"Total missed exclusivity threads: {len(missed)}")
    for item in missed:
        print(f"  [{item[0]}] Pattern: '{item[1]}' | Snippet: '{item[2]}' | Current V2: {item[3]}")
    return missed


def audit_auto_renewal():
    print("\n" + "=" * 70)
    print("2. AUDITING MISSED AUTO-RENEWAL CLAUSES")
    print("=" * 70)
    pats = [
        re.compile(r"auto-renew", re.I),
        re.compile(r"automatic\s+renewal", re.I),
        re.compile(r"renews?\s+automatically", re.I),
        re.compile(r"renews?\s+on\s+its\s+own", re.I),
        re.compile(r"continues?\s+(from\s+)?year\s+to\s+year", re.I),
        re.compile(r"renews?\s+every\s+year", re.I),
        re.compile(r"evergreen", re.I),
        re.compile(r"roll\s*over\s+automatically", re.I),
        re.compile(r"successive\s+(periods|years|months|terms)", re.I)
    ]
    missed = []
    for t in THREADS:
        tid = t["thread_id"]
        latest = split_latest(t["supplier_message"])
        if re.search(r"no\s+automatic\s+renewal|renewal\s+only\s+(by\s+mutual|if\s+both)|renew(al)?\s+by\s+mutual", latest, re.I):
            continue
        for p in pats:
            m = p.search(latest)
            if m:
                if "BANNED_TERM" not in V2_PREDS[tid] and "PROMPT_INJECTION" not in V2_PREDS[tid]:
                    snippet = latest[max(0, m.start()-30):min(len(latest), m.end()+40)].replace("\n", " ")
                    missed.append((tid, m.group(0), snippet, V2_PREDS[tid]))
                break

    print(f"Total missed auto-renewal threads: {len(missed)}")
    for item in missed:
        print(f"  [{item[0]}] Pattern: '{item[1]}' | Snippet: '{item[2]}' | Current V2: {item[3]}")
    return missed


def audit_advance_payments():
    print("\n" + "=" * 70)
    print("3. AUDITING MISSED ADVANCE PAYMENTS (>30%)")
    print("=" * 70)
    pats = [
        re.compile(r"(\d+)\s*%\s*(?:of\s+the\s+order\s+value\s+)?(?:upfront|advance|deposit|down\s*payment)", re.I),
        re.compile(r"(?:upfront|advance|deposit|down\s*payment)\s*(?:payment\s+)?(?:of\s+)?(\d+)\s*%", re.I),
        re.compile(r"\b(forty|fifty|sixty|seventy|eighty|ninety|thirty[- ]five)\s*%\s*(?:upfront|advance)", re.I),
        re.compile(r"\b(half|one[- ]third|third|two[- ]thirds)\s+(?:the\s+order\s+value\s+)?(?:upfront|advance|deposit)", re.I),
        re.compile(r"\b(upfront|advance|deposit)\s+of\s+(?:half|one[- ]third|third|two[- ]thirds)", re.I),
        re.compile(r"payment\s+terms:\s*(\d+)%\s*(?:advance|upfront)", re.I),
    ]
    missed = []
    for t in THREADS:
        tid = t["thread_id"]
        latest = split_latest(t["supplier_message"])
        for p in pats:
            m = p.search(latest)
            if m:
                # Extract pct if digit
                pct = None
                for g in m.groups():
                    if g and g.isdigit():
                        pct = int(g)
                        break
                is_over_30 = (pct is not None and pct > 30) or (pct is None)  # words like half, 40%, etc.
                if is_over_30:
                    if "BANNED_TERM" not in V2_PREDS[tid] and "PROMPT_INJECTION" not in V2_PREDS[tid]:
                        snippet = latest[max(0, m.start()-30):min(len(latest), m.end()+40)].replace("\n", " ")
                        missed.append((tid, m.group(0), snippet, V2_PREDS[tid]))
                break

    print(f"Total missed advance payment threads: {len(missed)}")
    for item in missed:
        print(f"  [{item[0]}] Pattern: '{item[1]}' | Snippet: '{item[2]}' | Current V2: {item[3]}")
    return missed


def audit_unlimited_liability():
    print("\n" + "=" * 70)
    print("4. AUDITING MISSED UNLIMITED LIABILITY CLAUSES")
    print("=" * 70)
    pats = [
        re.compile(r"liability\s+.*?\s+unlimited", re.I),
        re.compile(r"unlimited\s+liability", re.I),
        re.compile(r"uncapped\s+liability", re.I),
        re.compile(r"no\s+cap\s+on\s+(acme'?s\s+)?liability", re.I),
        re.compile(r"liability\s+shall\s+not\s+be\s+limited", re.I),
        re.compile(r"indemnif.*?\bwithout\s+(limit|cap)", re.I)
    ]
    missed = []
    for t in THREADS:
        tid = t["thread_id"]
        latest = split_latest(t["supplier_message"])
        for p in pats:
            m = p.search(latest)
            if m:
                if "BANNED_TERM" not in V2_PREDS[tid] and "PROMPT_INJECTION" not in V2_PREDS[tid]:
                    snippet = latest[max(0, m.start()-30):min(len(latest), m.end()+40)].replace("\n", " ")
                    missed.append((tid, m.group(0), snippet, V2_PREDS[tid]))
                break

    print(f"Total missed unlimited liability threads: {len(missed)}")
    for item in missed:
        print(f"  [{item[0]}] Pattern: '{item[1]}' | Snippet: '{item[2]}' | Current V2: {item[3]}")
    return missed


def audit_prompt_injections():
    print("\n" + "=" * 70)
    print("5. AUDITING PROMPT INJECTIONS & JAILBREAKS")
    print("=" * 70)
    # Search for any non-ASCII characters or suspicious terms anywhere in the thread
    pats = [
        ("NON_ASCII", re.compile(r"[^\x00-\x7F]")),
        ("AI_MODEL", re.compile(r"\b(language\s+model|llm|gpt|ai\s+assistant|ai\s+agent|ai\s+bot)\b", re.I)),
        ("INSTRUCTION", re.compile(r"\b(instruction\s+for|directives?\s+for|rules?\s+for\s+the\s+ai)\b", re.I)),
        ("SYSTEM_PROMPT", re.compile(r"\b(system\s+prompt|system\s+directive|system\s+note)\b", re.I)),
        ("OVERRIDE", re.compile(r"\b(override\s+playbook|admin\s+override|system\s+override|bypass\s+all)\b", re.I)),
        ("PREAPPROVED", re.compile(r"\b(pre[- ]approved|already\s+approved)\s+by\b", re.I)),
        ("BOT_SCREEN", re.compile(r"\b(whichever\s+bot|bot\s+screens|automated\s+system\s+is\s+reading)\b", re.I)),
    ]
    
    # Exceptions
    ALLOWED = [
        re.compile(r"\bAI-powered\b", re.I),
        re.compile(r"\bsystem\s+integration\b", re.I),
        re.compile(r"\bERP\s+system\b", re.I),
        re.compile(r"\b(assistant|administrative)\s+(manager|director|vp)\b", re.I),
        re.compile(r"\bexecutive\s+assistant\b", re.I),
    ]

    missed = []
    for t in THREADS:
        tid = t["thread_id"]
        msg = t["supplier_message"]
        if "PROMPT_INJECTION" in V2_PREDS[tid]:
            continue
            
        sanitized = msg
        for exc in ALLOWED:
            sanitized = exc.sub(" ", sanitized)

        for name, p in pats:
            if name == "NON_ASCII":
                # Find non-ascii chars that are not common currency or punctuation like ₹, —, –, ‘, ’, “, ”
                clean_punct = re.sub(r"[₹—–‘’“”•\s]", "", sanitized)
                m = p.search(clean_punct)
                if m:
                    idx = msg.find(m.group(0))
                    snippet = msg[max(0, idx-30):min(len(msg), idx+50)].replace("\n", " ")
                    missed.append((tid, f"MULTILINGUAL: '{m.group(0)}'", snippet, V2_PREDS[tid]))
                    break
            else:
                m = p.search(sanitized)
                if m:
                    snippet = msg[max(0, m.start()-30):min(len(msg), m.end()+50)].replace("\n", " ")
                    missed.append((tid, f"{name}: '{m.group(0)}'", snippet, V2_PREDS[tid]))
                    break

    print(f"Total potential missed injection threads: {len(missed)}")
    for item in missed:
        print(f"  [{item[0]}] {item[1]} | Snippet: '{item[2]}' | Current V2: {item[3]}")
    return missed


def audit_free_units_and_discounts():
    print("\n" + "=" * 70)
    print("6. AUDITING FREE UNITS, PACKS & VOLUME DISCOUNTS")
    print("=" * 70)
    free_pat = re.compile(r"(plus\s+\d+\s+free|free\s+\w+\s+for\s+every|buy\s+\d+\s+get)", re.I)
    vol_pat = re.compile(r"(\d+)%\s*(?:off|discount)\s+for\s+orders\s+of\s+(\d+)", re.I)
    pack_pat = re.compile(r"(per\s+box|per\s+pack|per\s+carton|per\s+case|per\s+set|per\s+pair)", re.I)

    free_matches = []
    vol_matches = []
    pack_matches = []

    for t in THREADS:
        tid = t["thread_id"]
        latest = split_latest(t["supplier_message"])
        
        m_free = free_pat.search(latest)
        if m_free:
            free_matches.append((tid, m_free.group(0), latest.replace("\n", " ")[:80], V2_PREDS[tid]))

        m_vol = vol_pat.search(latest)
        if m_vol:
            vol_matches.append((tid, m_vol.group(0), t["quantity"], int(m_vol.group(2)), V2_PREDS[tid]))

        m_pack = pack_pat.search(latest)
        if m_pack:
            pack_matches.append((tid, t["category"], m_pack.group(0), latest.replace("\n", " ")[:80], V2_PREDS[tid]))

    print(f"Total threads mentioning free units: {len(free_matches)}")
    print(f"Total threads mentioning volume discount: {len(vol_matches)}")
    print(f"Total threads mentioning pack/box: {len(pack_matches)}")
    
    return free_matches, vol_matches, pack_matches


if __name__ == "__main__":
    audit_exclusivity()
    audit_auto_renewal()
    audit_advance_payments()
    audit_unlimited_liability()
    audit_prompt_injections()
    audit_free_units_and_discounts()


def audit_unflagged_injections():
    print("\n" + "=" * 70)
    print("7. AUDITING SUSPICIOUS INJECTION KEYWORDS NOT FLAGGED IN V2")
    print("=" * 70)
    pats = [
        re.compile(r"\b(language\s+model|llm|gpt|ai\s+bot|ai\s+agent)\b", re.I),
        re.compile(r"\b(admin\s+override|system\s+override|override\s+playbook|bypass\s+all)\b", re.I),
        re.compile(r"\b(system\s+note|system\s+directive|note\s+to\s+ai)\b", re.I),
        re.compile(r"\b(pre[- ]approved|already\s+approved|prior\s+approval)\b", re.I),
        re.compile(r"\b(whichever\s+bot|bot\s+screens|automated\s+system\s+is\s+reading)\b", re.I),
        re.compile(r"\b(cfo|ceo|coo|cto|vp\s+of|board\s+of\s+directors)\b", re.I),
        re.compile(r"<!--.*?-->", re.I),
    ]
    allowed = [
        re.compile(r"\bAI-powered\b", re.I),
        re.compile(r"\bsystem\s+integration\b", re.I),
        re.compile(r"\bERP\s+system\b", re.I),
        re.compile(r"\bassistant\s+(manager|director)\b", re.I),
        re.compile(r"\bexecutive\s+assistant\b", re.I),
    ]

    hits = []
    for t in THREADS:
        tid = t["thread_id"]
        msg = t["supplier_message"]
        if "PROMPT_INJECTION" in V2_PREDS[tid]:
            continue

        for p in pats:
            m = p.search(msg)
            if m:
                # check if allowed
                surrounding = msg[max(0, m.start()-25):min(len(msg), m.end()+25)]
                if not any(al.search(surrounding) for al in allowed):
                    idx = m.start()
                    snippet = msg[max(0, idx-30):min(len(msg), idx+60)].replace("\n", " ")
                    hits.append((tid, m.group(0), snippet, V2_PREDS[tid]))
                    break

    print(f"Total unflagged injection candidates: {len(hits)}")
    for h in hits:
        print(f"  [{h[0]}] ({h[1]}): '{h[2]}' -> V2: {h[3]}")
    return hits


def audit_all_missing_info():
    print("\n" + "=" * 70)
    print("8. AUDITING ALL MISSING_INFO THREADS IN V2")
    print("=" * 70)
    missing_threads = [t for t in THREADS if V2_PREDS[t["thread_id"]] == "ESCALATE:MISSING_INFO:"]
    print(f"Total MISSING_INFO threads in V2: {len(missing_threads)}")

    reasons = Counter()
    for t in missing_threads:
        tid = t["thread_id"]
        latest = split_latest(t["supplier_message"]).strip()
        
        # Check why it's missing info
        # Unlisted currency?
        unlisted = re.search(r"\b(JPY|SGD|AUD|CAD|CHF|CNY|AED|SAR|NZD)\b", latest, re.I)
        # Subscription missing period?
        is_sub = t["category"] in ["cloud-servers", "crm-licenses", "design-software"]
        has_period = bool(re.search(r"(per\s+(year|month|yr|mo)|/yr|/mo)", latest, re.I))
        # No number at all?
        has_num = bool(re.search(r"\d+", latest))

        if unlisted:
            reasons["UNLISTED_CURRENCY"] += 1
        elif is_sub and not has_period:
            reasons["SUB_WITHOUT_PERIOD"] += 1
        elif not has_num:
            reasons["NO_NUMERIC_PRICE"] += 1
        else:
            reasons["OTHER_PARSER_FAILURE"] += 1
            print(f"  [OTHER] {tid} ({t['category']}): {latest[:100]}")

    print("Reasons breakdown:", dict(reasons))


def audit_gst_phrases():
    print("\n" + "=" * 70)
    print("9. AUDITING GST & TAX INCLUSION PHRASES")
    print("=" * 70)
    current_gst_re = re.compile(r"(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))", re.I)
    
    missed_gst = []
    for t in THREADS:
        tid = t["thread_id"]
        latest = split_latest(t["supplier_message"])
        if "gst" in latest.lower() or "tax" in latest.lower():
            if not current_gst_re.search(latest):
                # find sentence or line with gst or tax
                for line in latest.split("\n"):
                    if "gst" in line.lower() or "tax" in line.lower():
                        missed_gst.append((tid, line.strip(), t["category"], V2_PREDS[tid]))

    print(f"Total threads with uncaptured GST/tax lines: {len(missed_gst)}")
    for item in missed_gst[:40]:
        print(f"  [{item[0]}] ({item[2]}): '{item[1]}' [V2: {item[3]}]")
    return missed_gst
