import re

GST_INCLUSIVE_PATTERNS = [
    re.compile(r"\b(inclusive\s+of\s+GST|including\s+GST|\(?GST\s+included\)?|incl\.?\s+GST)\b", re.I)
]

GST_EXCLUSIVE_PATTERNS = [
    re.compile(r"\b(exclusive\s+of\s+GST|excluding\s+GST|excl\.?\s+GST|\+\s*GST|plus\s+GST|GST\s+extra)\b", re.I)
]

def is_gst_inclusive(text: str) -> bool:
    # First check explicit exclusive mentions
    if any(pat.search(text) for pat in GST_EXCLUSIVE_PATTERNS):
        return False
    return any(pat.search(text) for pat in GST_INCLUSIVE_PATTERNS)

positive_gst = [
    "INR 35,000 per seat per year incl. GST.",
    "Rs. 2,436 per box incl. GST.",
    "₹26,669 per phone incl GST.",
    "Rs. 95,813 per site per month incl. GST.",
    "INR 77,597 per laptop including GST.",
    "₹10,292 per chair inclusive of GST.",
    "INR 21,000 per monitor (GST included).",
    "INR 21,000 per monitor GST included.",
]

negative_gst = [
    "INR 35,000 per seat per year excl. GST.",
    "Rs. 2,436 per box excl GST.",
    "₹26,669 per phone excluding GST.",
    "Rs. 95,813 per site per month exclusive of GST.",
    "INR 77,597 per laptop + GST.",
    "₹10,292 per chair plus GST.",
    "INR 21,000 per monitor, GST extra.",
    "Standard pricing in INR without tax mention."
]

print("--- TESTING GST POSITIVE CASES (EXPECT TRUE) ---")
for text in positive_gst:
    inc = is_gst_inclusive(text)
    print(f"[{'PASS' if inc else 'FAIL'}] '{text}' -> Inclusive: {inc}")

print("\n--- TESTING GST NEGATIVE CASES (EXPECT FALSE) ---")
for text in negative_gst:
    inc = is_gst_inclusive(text)
    print(f"[{'PASS' if not inc else 'FAIL'}] '{text}' -> Inclusive: {inc}")
