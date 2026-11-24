import sys, re, csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'src'))

from procurement.data_loader import load_threads
from scripts.build_experimental_v2 import RefinedDecisionEngine
from procurement.decision_engine import DecisionEngine

threads = load_threads(Path('data/raw/threads.csv'))
engine_v1 = DecisionEngine()
engine_v2 = RefinedDecisionEngine()

vol_threads = []
for t in threads:
    m = re.search(r'with\s+a\s+further\s+(\d+)\s*%\s*off\s+for\s+orders\s+of\s+(\d+)\s+([a-zA-Z\s]+?)\s+or\s+more', t['supplier_message'], re.I)
    if m:
        pct = int(m.group(1))
        thresh = int(m.group(2))
        qty = t['quantity']
        if qty >= thresh:
            vol_threads.append((t, pct, thresh))

print(f"Total volume discount threads meeting threshold: {len(vol_threads)}")

headers = f"{'TID':<8} | {'Qty':<5} | {'Thresh':<6} | {'Disc':<5} | {'V1 Prediction':<32} | {'V2 Prediction':<32} | {'Changed?'}"
print(headers)
print("-" * len(headers))

changed_count = 0
reasons_for_change = []

for t, pct, thresh in vol_threads:
    tid = t['thread_id']
    v1_lbl, v1_aud = engine_v1.decide(t)
    v2_lbl, v2_aud = engine_v2.decide(t)
    is_diff = (v1_lbl != v2_lbl)
    if is_diff:
        changed_count += 1
        reasons_for_change.append((tid, v1_lbl, v2_lbl, v1_aud, v2_aud))
    diff_mark = "YES" if is_diff else "NO (same decision)"
    print(f"{tid:<8} | {t['quantity']:5} | {thresh:6} | {pct:4}% | {v1_lbl:<32} | {v2_lbl:<32} | {diff_mark}")

print(f"\nTotal volume discount threads where prediction changed: {changed_count}/{len(vol_threads)}")

if reasons_for_change:
    print("\nDetailed explanation of changes:")
    for tid, v1, v2, aud1, aud2 in reasons_for_change:
        print(f"\n=== {tid} ===")
        print(f"  V1: {v1} (p={aud1.get('p')}, L={aud1.get('concession_level')}, deal={aud1.get('deal_value')}, limit={aud1.get('approval_limit')})")
        print(f"  V2: {v2} (p={aud2.get('p')}, L={aud2.get('concession_level')}, deal={aud2.get('deal_value')}, limit={aud2.get('approval_limit')})")
