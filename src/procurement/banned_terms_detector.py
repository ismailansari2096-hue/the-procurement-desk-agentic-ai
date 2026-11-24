"""
Banned Contract Terms Detector.
Evaluates ONLY the latest message for illegal clauses.
Governed by policies/banned-terms.md.
"""

import re
from typing import Tuple


class BannedTermsDetector:
    # 1. Auto-renewal in any wording
    # Allowed: "renewal only by mutual agreement", "no automatic renewal", "renewal only if both parties sign again"
    ALLOWED_RENEWAL = [
        re.compile(r"no\s+automatic\s+renewal", re.I),
        re.compile(r"renewal\s+only\s+(by\s+mutual\s+agreement|if\s+both\s+parties)", re.I),
        re.compile(r"renew(al)?\s+by\s+mutual\s+consent", re.I),
    ]
    BANNED_RENEWAL = [
        re.compile(r"\bauto-renews\b", re.I),
        re.compile(r"\bauto-renew\b", re.I),
        re.compile(r"\bautomatic\s+renewal\b", re.I),
        re.compile(r"renews?\s+automatically\b", re.I),
        re.compile(r"renews?\s+on\s+its\s+own\b", re.I),
        re.compile(r"continues?\s+(from\s+)?year\s+to\s+year\s+unless\b", re.I),
        re.compile(r"renews?\s+every\s+year\s+unless\b", re.I),
    ]

    # 2. Upfront or advance payment above 30%
    # Allowed: advance or upfront of 30% or less (e.g. 10%, 20%, 25%, 30%)
    # Words for numbers above 30: 31..99, forty, fifty, sixty, seventy, eighty, ninety, etc.
    ADVANCE_PATTERN = re.compile(r"(\d+)\s*%\s*(of\s+the\s+order\s+value\s+)?(upfront|advance)|\b(upfront|advance)\s*(payment\s+)?(of\s+)?(\d+)\s*%", re.I)
    ADVANCE_WORDS = [
        (re.compile(r"\b(forty|fifty|sixty|seventy|eighty|ninety|thirty[- ]five)\s*%\s*(of\s+the\s+order\s+value\s+)?(upfront|advance)", re.I)),
        (re.compile(r"\b(upfront|advance)\s*(payment\s+)?(of\s+)?(forty|fifty|sixty|seventy|eighty|ninety|thirty[- ]five)\s*%", re.I))
    ]

    # 3. Unlimited liability for Acme
    BANNED_LIABILITY = [
        re.compile(r"unlimited\s+liability\s+for\s+acme", re.I),
        re.compile(r"acme\s+(assumes|bears|accepts)\s+unlimited\s+liability", re.I),
    ]

    # 4. Exclusivity: Acme must buy only from this supplier
    # Allowed: "We are not asking for exclusivity", "No exclusivity is asked", "without exclusivity"
    ALLOWED_EXCLUSIVITY = [
        re.compile(r"(we\s+are\s+)?not\s+asking\s+for\s+exclusivity", re.I),
        re.compile(r"no\s+exclusivity\s+(is\s+asked|required|requested)", re.I),
        re.compile(r"without\s+exclusivity", re.I),
    ]
    BANNED_EXCLUSIVITY = [
        re.compile(r"exclusive\s+supplier", re.I),
        re.compile(r"exclusive\s+deal", re.I),
        re.compile(r"exclusive\s+partnership", re.I),
        re.compile(r"acme\s+must\s+buy\s+only\s+from", re.I),
        re.compile(r"acme\s+agrees\s+to\s+use\s+us\s+as\s+its\s+exclusive", re.I),
    ]

    def has_banned_term(self, latest_message: str) -> Tuple[bool, str]:
        if not latest_message:
            return False, ""

        # Check Exclusivity
        is_exclusivity_allowed = any(pat.search(latest_message) for pat in self.ALLOWED_EXCLUSIVITY)
        if not is_exclusivity_allowed:
            for pat in self.BANNED_EXCLUSIVITY:
                m = pat.search(latest_message)
                if m:
                    return True, f"Exclusivity clause detected: '{m.group(0)}'"

        # Check Auto-Renewal
        is_renewal_allowed = any(pat.search(latest_message) for pat in self.ALLOWED_RENEWAL)
        if not is_renewal_allowed:
            for pat in self.BANNED_RENEWAL:
                m = pat.search(latest_message)
                if m:
                    return True, f"Auto-renewal clause detected: '{m.group(0)}'"

        # Check Advance > 30%
        for m in self.ADVANCE_PATTERN.finditer(latest_message):
            pct_str = m.group(1) or m.group(7)
            if pct_str:
                pct = int(pct_str)
                if pct > 30:
                    return True, f"Advance payment above 30% detected ({pct}%)"

        for pat in self.ADVANCE_WORDS:
            m = pat.search(latest_message)
            if m:
                return True, f"Advance payment above 30% in words detected: '{m.group(0)}'"

        # Check Unlimited Liability
        for pat in self.BANNED_LIABILITY:
            m = pat.search(latest_message)
            if m:
                return True, f"Unlimited liability clause detected: '{m.group(0)}'"

        return False, ""
