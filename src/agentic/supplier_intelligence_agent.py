"""
Supplier Intelligence Agent.
Responsible for maintaining supplier registry state, identity lookup,
blacklist/probation status verification, currency exchange rate overrides,
and contracted price ceilings.
"""

from typing import Optional, Dict, Any
from procurement.policy_engine import PolicyEngine
from agentic.models import SupplierIntelligenceOutput


class SupplierIntelligenceAgent:
    """
    Audits supplier profiles, vendor reputations, and contracted relationships.
    """

    def __init__(self, policy_engine: Optional[PolicyEngine] = None):
        self.pe = policy_engine or PolicyEngine()

    def inspect_supplier(self, supplier_name: str) -> SupplierIntelligenceOutput:
        """
        Inspect supplier registry and return supplier intelligence metrics.
        """
        status = self.pe.get_supplier_status(supplier_name)
        supp = self.pe.suppliers.get(supplier_name, {})

        status_upper = status.upper().strip()
        is_blacklisted = (status_upper == "BLACKLISTED")
        is_probation = (status_upper == "PROBATION")

        price_cap = supp.get("price_cap")
        custom_fx = supp.get("custom_fx", {})

        metadata = {
            "registered": supplier_name in self.pe.suppliers,
            "status": status,
            "notes": supp.get("notes", "")
        }

        return SupplierIntelligenceOutput(
            supplier_name=supplier_name,
            status=status,
            is_blacklisted=is_blacklisted,
            is_probation=is_probation,
            price_cap=price_cap,
            custom_fx=custom_fx,
            metadata=metadata
        )
