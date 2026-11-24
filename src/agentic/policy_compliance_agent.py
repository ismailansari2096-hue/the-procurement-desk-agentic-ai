"""
Policy Compliance Agent.
Responsible for resolving category policies, temporal amendments as of thread date,
contract overrides, and scanning for banned contractual clauses (auto-renewal,
advance payment >30%, Acme's liability uncapped, and exclusivity).
"""

import re
from typing import Optional, Dict, Any, List
from procurement.policy_engine import PolicyEngine
from procurement.banned_terms_detector import BannedTermsDetector
from agentic.models import PolicyComplianceOutput


class PolicyComplianceAgent:
    """
    Enforces governance, category baseline limits, dated policy amendments,
    and contractual term restrictions.
    """

    ADDITIONAL_LIABILITY = [
        re.compile(r"acme'?s\s+liability\s+.*?\s+unlimited", re.I),
    ]
    ADDITIONAL_ADVANCE = [
        re.compile(r"\bhalf\s+(the\s+order\s+value\s+)?(upfront|advance)\b", re.I),
        re.compile(r"\b(upfront|advance)\s+.*?half\b", re.I),
        re.compile(r"payment\s+terms:\s*60%\s*advance", re.I),
    ]
    # V3 Exclusivity Refinements
    ADDITIONAL_ALLOWED_EXCLUSIVITY = [
        re.compile(r"\bnon-exclusive\b", re.I),
        re.compile(r"\bnot\s+exclusive\b", re.I),
        re.compile(r"acme\s+(will\s+not|is\s+not\s+required\s+to|does\s+not\s+have\s+to|need\s+not)\s+buy\s+only\s+from", re.I),
        re.compile(r"(not|never)\s+(obligated|required)\s+to\s+(buy|purchase)\s+only\s+from", re.I),
    ]
    ADDITIONAL_EXCLUSIVITY = [
        re.compile(r"\bacme\s+(must|will|agrees\s+to|shall)\s+buy\s+(these\s+items\s+)?only\s+from\b", re.I),
        re.compile(r"\b(buy|purchase)\s+(these\s+items\s+)?only\s+from\s+us\b", re.I),
    ]

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        enable_refined_banned: bool = True,
        enable_v3_exclusivity: bool = False
    ):
        self.pe = policy_engine or PolicyEngine()
        self.banned_detector = BannedTermsDetector()
        self.enable_refined_banned = enable_refined_banned
        self.enable_v3_exclusivity = enable_v3_exclusivity

    def evaluate_compliance(
        self,
        category_id: str,
        thread_date: str,
        supplier_name: str,
        latest_message: str
    ) -> PolicyComplianceOutput:
        """
        Resolves effective policy parameters and audits latest message for banned clauses.
        """
        base_cat = self.pe.categories.get(category_id, {})
        base_target = float(base_cat.get("target_price", 0.0))
        base_walkaway = float(base_cat.get("walkaway_price", 0.0))
        base_rounds = int(base_cat.get("rounds", 3))
        base_beta = float(base_cat.get("beta", 1.0))
        base_approval = float(base_cat.get("approval_limit", 100000.0))

        # Effective policy with amendments and supplier overrides
        effective_policy = self.pe.get_effective_policy(category_id, thread_date, supplier_name)

        active_amendments = [
            amd for amd in self.pe.amendments
            if amd.get("category") == category_id and amd.get("effective_date", "") <= thread_date
        ]

        # Scan for banned terms in latest message
        has_banned, banned_reason = self.banned_detector.has_banned_term(latest_message)
        banned_clause = ""

        # V3 Negation Filter: suppress false positive exclusivity if explicit non-exclusivity is stated
        if has_banned and self.enable_v3_exclusivity and "Exclusivity clause detected" in banned_reason:
            if any(pat.search(latest_message) for pat in self.ADDITIONAL_ALLOWED_EXCLUSIVITY):
                has_banned = False
                banned_reason = ""

        if not has_banned and self.enable_refined_banned:
            for pat in self.ADDITIONAL_LIABILITY:
                m = pat.search(latest_message)
                if m:
                    has_banned = True
                    banned_reason = f"Unlimited liability clause detected: '{m.group(0)}'"
                    banned_clause = m.group(0)
                    break

            if not has_banned:
                for pat in self.ADDITIONAL_ADVANCE:
                    m = pat.search(latest_message)
                    if m:
                        has_banned = True
                        banned_reason = f"Advance payment above 30% detected: '{m.group(0)}'"
                        banned_clause = m.group(0)
                        break

        # V3 Refined Exclusivity Detection with Negation Awareness
        if not has_banned and self.enable_v3_exclusivity:
            is_excl_allowed = (
                any(pat.search(latest_message) for pat in self.banned_detector.ALLOWED_EXCLUSIVITY)
                or any(pat.search(latest_message) for pat in self.ADDITIONAL_ALLOWED_EXCLUSIVITY)
            )
            if not is_excl_allowed:
                for pat in self.ADDITIONAL_EXCLUSIVITY:
                    m = pat.search(latest_message)
                    if m:
                        has_banned = True
                        banned_reason = f"Exclusivity clause detected: '{m.group(0)}'"
                        banned_clause = m.group(0)
                        break

        return PolicyComplianceOutput(
            category_id=category_id,
            category_name=base_cat.get("id", category_id),
            base_target=base_target,
            base_walkaway=base_walkaway,
            base_rounds=base_rounds,
            base_beta=base_beta,
            base_approval_limit=base_approval,
            effective_target=float(effective_policy["target_price"]),
            effective_walkaway=float(effective_policy["walkaway_price"]),
            effective_rounds=int(effective_policy["rounds"]),
            effective_beta=float(effective_policy.get("beta", base_beta)),
            effective_approval_limit=float(effective_policy["approval_limit"]),
            is_probation=bool(effective_policy.get("is_probation", False)),
            active_amendments=active_amendments,
            banned_term_detected=has_banned,
            banned_term_reason=banned_reason,
            banned_term_clause=banned_clause
        )
