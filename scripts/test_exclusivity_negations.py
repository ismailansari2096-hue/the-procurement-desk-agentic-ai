import re

# Refined Exclusivity Patterns
ALLOWED_EXCLUSIVITY = [
    re.compile(r"(we\s+are\s+)?not\s+asking\s+for\s+exclusivity", re.I),
    re.compile(r"no\s+exclusivity\s+(is\s+asked|required|requested)", re.I),
    re.compile(r"without\s+exclusivity", re.I),
    re.compile(r"\bnon-exclusive\b", re.I),
    re.compile(r"\bnot\s+exclusive\b", re.I),
    re.compile(r"acme\s+(will\s+not|is\s+not\s+required\s+to|does\s+not\s+have\s+to|need\s+not)\s+buy\s+only\s+from", re.I),
    re.compile(r"(not|never)\s+(obligated|required)\s+to\s+(buy|purchase)\s+only\s+from", re.I),
]

BANNED_EXCLUSIVITY = [
    re.compile(r"\bexclusive\s+supplier\b", re.I),
    re.compile(r"\bexclusive\s+deal\b", re.I),
    re.compile(r"\bexclusive\s+partnership\b", re.I),
    re.compile(r"\bacme\s+(must|will|agrees\s+to|shall)\s+buy\s+(these\s+items\s+)?only\s+from\b", re.I),
    re.compile(r"\bacme\s+agrees\s+to\s+use\s+us\s+as\s+its\s+exclusive\b", re.I),
    re.compile(r"\b(buy|purchase)\s+(these\s+items\s+)?only\s+from\s+us\b", re.I),
]

def check_exclusivity(msg: str):
    is_allowed = any(pat.search(msg) for pat in ALLOWED_EXCLUSIVITY)
    if is_allowed:
        return False, "Allowed exclusivity statement"
    for pat in BANNED_EXCLUSIVITY:
        m = pat.search(msg)
        if m:
            return True, f"Banned exclusivity: '{m.group(0)}'"
    return False, "No exclusivity mentioned"

# Test positive cases (should be banned)
positive_cases = [
    "Acme must buy only from this supplier.",
    "Acme will buy these items only from us for the next two years.",
    "As part of the terms, Acme agrees to buy only from us.",
    "We expect you to buy these items only from us.",
    "You agree to purchase only from us going forward.",
    "Acme agrees to use us as its exclusive provider.",
    "This is an exclusive supplier agreement."
]

# Test negative cases (should NOT be banned / allowed)
negative_cases = [
    "We are not asking for exclusivity.",
    "No exclusivity is asked.",
    "Without exclusivity, our price is ₹50,000.",
    "Acme will not buy only from us; you are free to use other vendors.",
    "Acme is not required to buy only from us.",
    "Acme does not have to buy only from us.",
    "This is a non-exclusive partnership.",
    "Our agreement is not exclusive.",
    "Standard pricing without exclusivity clauses."
]

print("--- TESTING POSITIVE CASES (EXPECT BANNED=TRUE) ---")
for text in positive_cases:
    banned, reason = check_exclusivity(text)
    print(f"[{'PASS' if banned else 'FAIL'}] '{text}' -> Banned: {banned} ({reason})")

print("\n--- TESTING NEGATIVE CASES (EXPECT BANNED=FALSE) ---")
for text in negative_cases:
    banned, reason = check_exclusivity(text)
    print(f"[{'PASS' if not banned else 'FAIL'}] '{text}' -> Banned: {banned} ({reason})")
