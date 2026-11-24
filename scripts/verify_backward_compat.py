import sys, csv, hashlib
sys.path.insert(0, 'src')
from agentic.orchestrator import NegotiationOrchestrator

with open('data/raw/threads.csv', encoding='utf-8') as f:
    threads = list(csv.DictReader(f))

# Verify V1
orch_v1 = NegotiationOrchestrator(mode='v1')
v1_preds = [t['thread_id'] + ',' + orch_v1.decide(t) for t in threads]
v1_csv = 'thread_id,label\n' + '\n'.join(v1_preds) + '\n'
v1_hash = hashlib.sha256(v1_csv.encode('utf-8')).hexdigest()
orig_v1_hash = hashlib.sha256(open('outputs/submission.csv', 'rb').read()).hexdigest()
print(f'V1 reproduction match: {v1_hash == orig_v1_hash} ({v1_hash})')

# Verify V2
orch_v2 = NegotiationOrchestrator(mode='v2')
v2_preds = [t['thread_id'] + ',' + orch_v2.decide(t) for t in threads]
v2_csv = 'thread_id,label\n' + '\n'.join(v2_preds) + '\n'
v2_hash = hashlib.sha256(v2_csv.encode('utf-8')).hexdigest()
orig_v2_hash = hashlib.sha256(open('outputs/experimental/submission_v2.csv', 'rb').read()).hexdigest()
print(f'V2 reproduction match: {v2_hash == orig_v2_hash} ({v2_hash})')

# Verify V3
orch_v3 = NegotiationOrchestrator(mode='v3')
v3_preds = [t['thread_id'] + ',' + orch_v3.decide(t) for t in threads]
v3_csv = 'thread_id,label\n' + '\n'.join(v3_preds) + '\n'
v3_hash = hashlib.sha256(v3_csv.encode('utf-8')).hexdigest()
orig_v3_hash = hashlib.sha256(open('outputs/experimental/submission_v3.csv', 'rb').read()).hexdigest()
print(f'V3 reproduction match: {v3_hash == orig_v3_hash} ({v3_hash})')
