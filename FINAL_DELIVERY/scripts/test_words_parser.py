import re
from pathlib import Path
import sys
sys.path.insert(0, 'src')
from procurement.data_loader import load_threads

def words_to_number(text: str):
    units = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
        'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
    }
    multipliers = {'hundred': 100, 'thousand': 1000, 'lakh': 100000, 'lakhs': 100000}
    
    cleaned_text = text.replace('-', ' ').lower()
    tokens = re.findall(r'[a-zA-Z]+', cleaned_text)
    total = 0
    current = 0
    found_any = False
    
    for token in tokens:
        if token in units:
            current += units[token]
            found_any = True
        elif token == 'hundred':
            if current == 0:
                current = 1
            current *= 100
            found_any = True
        elif token in ['thousand', 'lakh', 'lakhs']:
            if current == 0:
                current = 1
            total += current * multipliers[token]
            current = 0
            found_any = True
        elif token in ['and', 'rupees', 'inr', 'rs', 'dollars', 'usd', 'euros', 'eur', 'pounds', 'gbp']:
            continue
        else:
            break
            
    total += current
    return total if found_any else None

threads = load_threads(Path('data/raw/threads.csv'))
parsed_count = 0
word_tokens = r'(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|lakh|lakhs|and|[a-zA-Z]+-[a-zA-Z]+)'
pattern = re.compile(rf'(?:is|quote|offer|can do|at)\s+({word_tokens}+(?:\s+{word_tokens}+)*)\s*(?:rupees|inr|rs\.?|dollars|usd|euros|eur|pounds|gbp)?\s*(?:per\s+[a-zA-Z\s]+)?', re.I)

for t in threads:
    m = pattern.search(t['supplier_message'])
    if m:
        val = words_to_number(m.group(1))
        if val:
            parsed_count += 1
            if parsed_count <= 10:
                print(f"{t['thread_id']}: '{m.group(1).strip()}' -> {val}")

print(f"Total words-to-number matched: {parsed_count}")
