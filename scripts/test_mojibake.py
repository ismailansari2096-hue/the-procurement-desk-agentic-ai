import re

text_euro = "We can offer € 50 per seat."
text_pound = "We can offer £ 50 per seat."
text_rupee = "We can offer ₹ 50 per seat."
text_emdash = "CORRECTION — the price should read ₹ 50"

# What is in thread_parser.py:
pat_eur = r"\bEUR\b|â‚¬"
pat_gbp = r"\bGBP\b|Â£"
pat_corr = r"CORRECTION\s*â€”\s*the\s+price"

print("pat_eur matches text_euro?", bool(re.search(pat_eur, text_euro)))
print("pat_gbp matches text_pound?", bool(re.search(pat_gbp, text_pound)))
print("pat_corr matches text_emdash?", bool(re.search(pat_corr, text_emdash)))
