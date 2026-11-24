"""
Data Loader for The Procurement Desk.
Loads competition datasets safely using csv.DictReader to handle multi-line threads.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any
from procurement.config import DATA_DIR, RAW_DATA_DIR


def load_threads(file_path: Path) -> List[Dict[str, Any]]:
    """Load threads from CSV, returning list of row dictionaries."""
    if not file_path.exists():
        raise FileNotFoundError(f"Thread file not found: {file_path}")

    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "thread_id": row["thread_id"].strip(),
                "date": row["date"].strip(),
                "supplier": row["supplier"].strip(),
                "category": row["category"].strip(),
                "quantity": int(row["quantity"].strip()),
                "round": int(row["round"].strip()),
                "our_last_counter": float(row["our_last_counter"].strip()) if row.get("our_last_counter") else None,
                "supplier_message": row["supplier_message"]
            })
    return records


def load_sample_answers(file_path: Path = None) -> Dict[str, str]:
    """Load ground truth answers mapping thread_id -> label."""
    if file_path is None:
        file_path = RAW_DATA_DIR / "sample_answers.csv"
    if not file_path.exists():
        return {}

    answers = {}
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            answers[row["thread_id"].strip()] = row["label"].strip()
    return answers
