"""
Policy Engine for resolving effective category limits and supplier terms.
Resolves:
- Base category values
- Dated amendments on or before thread date (chronological precedence)
- Supplier contract overrides (cap replacing walkaway, custom FX rates)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from procurement.config import KB_DIR


class PolicyEngine:
    def __init__(self, kb_path: Path = KB_DIR):
        with open(kb_path / "categories.json", "r", encoding="utf-8") as f:
            self.categories: Dict[str, Dict[str, Any]] = json.load(f)

        with open(kb_path / "amendments.json", "r", encoding="utf-8") as f:
            self.amendments = json.load(f)

        with open(kb_path / "supplier_registry.json", "r", encoding="utf-8") as f:
            self.suppliers: Dict[str, Dict[str, Any]] = json.load(f)

        # Standard currency table from units-and-currency.md
        self.standard_fx = {
            "USD": 84.5,
            "EUR": 91.0,
            "GBP": 106.0,
            "INR": 1.0,
            "RS": 1.0,
            "RS.": 1.0,
            "₹": 1.0
        }

    def get_supplier_status(self, supplier_name: str) -> str:
        supp = self.suppliers.get(supplier_name)
        if not supp:
            return "Approved"
        return supp.get("status", "Approved")

    def get_effective_policy(self, category_id: str, thread_date: str, supplier_name: str) -> Dict[str, Any]:
        """Resolve all parameters for category at thread_date taking amendments and supplier contract into account."""
        if category_id not in self.categories:
            raise ValueError(f"Unknown category: {category_id}")

        base = dict(self.categories[category_id])

        # Filter amendments for this category on or before thread_date
        # Later amendments replace earlier ones
        applicable_amds = [
            a for a in self.amendments
            if a["category"] == category_id and a["effective_date"] <= thread_date
        ]
        # Sort by effective_date ascending
        applicable_amds.sort(key=lambda x: x["effective_date"])
        for amd in applicable_amds:
            field = amd.get("field")
            val = amd.get("value")
            if field and val:
                base[field] = val

        # Supplier contract overrides: price cap for category replaces walk-away price
        supp = self.suppliers.get(supplier_name, {})
        price_cap = supp.get("price_cap")
        if price_cap and price_cap.get("category") == category_id:
            base["walkaway_price"] = price_cap["cap"]

        # Check probation
        status = supp.get("status", "Approved")
        base["is_probation"] = (status == "PROBATION")
        base["supplier_status"] = status

        return base

    def get_exchange_rate(self, currency: str, supplier_name: str) -> Optional[float]:
        """Get FX rate for currency, checking supplier contract overrides first."""
        curr_upper = currency.upper().strip()
        supp = self.suppliers.get(supplier_name, {})
        custom_fx = supp.get("custom_fx", {})
        if curr_upper in custom_fx:
            return custom_fx[curr_upper]

        if curr_upper in self.standard_fx:
            return self.standard_fx[curr_upper]

        # Any other currency is unknown / missing info
        return None
