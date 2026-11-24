import sys, re
sys.path.insert(0, 'src')
from procurement.data_loader import load_threads
from pathlib import Path

threads = load_threads(Path('data/raw/threads.csv'))

non_ascii = []
for t in threads:
    # check for devanagari / non-latin scripts
    if re.search(r'[\u0900-\u097F\u0600-\u06FF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]', t['supplier_message']):
        non_ascii.append((t['thread_id'], t['supplier_message']))

print(f"Total threads with non-Latin scripts (Devanagari, Arabic, CJK): {len(non_ascii)}")
for tid, msg in non_ascii:
    print(f"=== {tid} ===")
    for line in msg.split("\n"):
        if re.search(r'[\u0900-\u097F\u0600-\u06FF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]', line):
            print("  ->", repr(line))
