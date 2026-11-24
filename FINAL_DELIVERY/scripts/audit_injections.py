import sys, re
sys.path.insert(0, 'src')
from procurement.data_loader import load_threads
from procurement.injection_detector import InjectionDetector
from pathlib import Path

threads = load_threads(Path('data/raw/threads.csv'))
detector = InjectionDetector()

detected = []
missed_candidates = []

injection_keywords = [
    r'ai\s+agent', r'system\s+note', r'pre-approved', r'cfo', r'prompt', r'instruction',
    r'ignore', r'disregard', r'override', r'approve', r'accept\s+this', r'output\s+accept',
    r'सहायक', r'निर्देश'
]
kw_re = re.compile('|'.join(injection_keywords), re.I)

for t in threads:
    msg = t['supplier_message']
    is_inj, reason = detector.is_injection(msg)
    if is_inj:
        detected.append((t['thread_id'], reason))
    else:
        # Check if suspicious keywords appear outside allowed exceptions
        if kw_re.search(msg):
            # Check if it has something suspicious
            missed_candidates.append((t['thread_id'], msg))

print(f"Already detected by InjectionDetector: {len(detected)}")
print(f"Suspicious candidates not detected: {len(missed_candidates)}")

for tid, msg in missed_candidates:
    for line in msg.split("\n"):
        if kw_re.search(line):
            # Check if this line is just an allowed exception
            if any(exc.search(line) for exc in detector.EXCEPTIONS):
                continue
            print(f"{tid}: {repr(line.strip())}")
