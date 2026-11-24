import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("./src").resolve()))

import csv
import re
from procurement.data_loader import load_threads
import src.procurement.thread_parser as tp_module

threads = load_threads(Path("data/raw/threads.csv"))
t10290 = next(t for t in threads if t["thread_id"] == "T10290")

pe = tp_module.PolicyEngine()
tp = tp_module.ThreadParser(pe)

price, err, debug = tp.extract_latest_offer(
    raw_thread=t10290["supplier_message"],
    supplier_name=t10290["supplier"],
    category_id=t10290["category"],
    thread_date=t10290["date"],
    quantity=int(t10290["quantity"])
)

print(f"Original parsed price: {price}, err: {err}")
latest_msg, _ = tp.split_messages(t10290["supplier_message"])
print(f"Latest msg:\n{latest_msg}")
print(f"Has 'incl. GST': {bool(re.search(r'incl\.?\s+GST', latest_msg, re.I))}")
