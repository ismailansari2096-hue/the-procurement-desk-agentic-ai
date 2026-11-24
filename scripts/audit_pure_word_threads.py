import sys, csv, re, copy
sys.path.insert(0, 'src')
from procurement.thread_parser import ThreadParser
from procurement.policy_engine import PolicyEngine
from agentic.orchestrator import NegotiationOrchestrator

pe = PolicyEngine()
orch_v3 = NegotiationOrchestrator(mode='v3')

with open('data/raw/threads.csv', encoding='utf-8') as f:
    threads = list(csv.DictReader(f))

word_tokens_robust = r'(?:thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|lakh|lakhs|twelve|eleven|zero|one|two|three|four|five|six|seven|eight|nine|ten)'

pure_word_tids = []
for t in threads:
    tid = t['thread_id']
    latest_msg, _ = ThreadParser(pe).split_messages(t['supplier_message'])
    has_digit = bool(re.search(r'(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)\s*[\d,]+(?:\.\d+)?', latest_msg))
    if not has_digit:
        clean = latest_msg.replace('-', ' ')
        m = re.search(rf'(?:is|quote|offer|can do|at)\s+({word_tokens_robust}+(?:\s+(?:and\s+)?{word_tokens_robust}+)*)\s*(?:rupees|inr|rs\.?|dollars|usd|euros|eur|pounds|gbp)?\s*(?:per\s+[a-zA-Z\s]+)?', clean, re.I)
        if m:
            pure_word_tids.append(tid)

print(f'Total pure word-quoted threads: {len(pure_word_tids)}')

word_audit = []
for tid in pure_word_tids:
    t = next(x for x in threads if x['thread_id'] == tid)
    res_v3, trace = orch_v3.process_thread(t)
    
    latest_msg, _ = ThreadParser(pe).split_messages(t['supplier_message'])
    clean = latest_msg.replace('-', ' ')
    m = re.search(rf'(?:is|quote|offer|can do|at)\s+({word_tokens_robust}+(?:\s+(?:and\s+)?{word_tokens_robust}+)*)\s*(?:rupees|inr|rs\.?|dollars|usd|euros|eur|pounds|gbp)?\s*(?:per\s+[a-zA-Z\s]+)?', clean, re.I)
    val = ThreadParser(pe).words_to_number(m.group(1))
    
    cat = t['category']
    supp = t['supplier']
    date = t['date']
    qty = int(t['quantity'])
    rnd = int(t['round'])
    pol = pe.get_effective_policy(cat, date, supp)
    unit = pol.get('unit', '').lower()
    gst_rate = pol.get('gst_rate', 0.18)
    
    p = val
    if re.search(r'per\s+dozen', latest_msg, re.I):
        p /= 12.0
    if cat == 'led-lighting' and re.search(r'per\s+pack', latest_msg, re.I):
        p /= 4.0
    if cat == 'printer-paper' and re.search(r'per\s+ream', latest_msg, re.I):
        p *= 10.0
    if 'per year' in unit and re.search(r'per\s+month\b|/mo\b', latest_msg, re.I):
        p *= 12.0
    elif 'per month' in unit and re.search(r'per\s+year\b|/yr\b', latest_msg, re.I):
        p /= 12.0
    if re.search(r'(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))', latest_msg, re.I):
        p /= (1.0 + gst_rate)
    
    th_out = copy.copy(trace['thread_understanding'])
    th_out.effective_inr_price = p
    
    pr_out = orch_v3.pricing_agent.negotiate(
        round_num=rnd,
        quantity=qty,
        normalized_offer_inr=p,
        policy_info=trace['policy_compliance'],
        supplier_info=trace['supplier_intelligence']
    )
    
    dec_out = orch_v3.validation_agent.validate_and_finalize(
        thread_id=tid,
        thread_output=th_out,
        supplier_output=trace['supplier_intelligence'],
        policy_output=trace['policy_compliance'],
        injection_output=trace['injection_defense'],
        pricing_output=pr_out
    )
    
    if dec_out.label != res_v3.label:
        word_audit.append((tid, cat, supp, rnd, qty, trace['thread_understanding'].effective_inr_price, p, res_v3.label, dec_out.label, m.group(1)))

print(f'Actual decision changes on pure word threads: {len(word_audit)}')
for wa in word_audit:
    print(f'{wa[0]}: {wa[1]} | {wa[2]} | Rnd {wa[3]} | Qty {wa[4]}')
    print(f'   phrase: "{wa[9]}"')
    print(f'   price: {wa[5]} -> {wa[6]}')
    print(f'   V3: {wa[7]} -> V4: {wa[8]}')
    print('-'*50)
