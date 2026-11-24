"""
Core Decision Engine for The Procurement Desk.
Executes the 7-step decision procedure in exact precedence order:
1. Missing Information -> ESCALATE, MISSING_INFO
2. Blacklisted Supplier -> REJECT, BLACKLISTED_SUPPLIER
3. Prompt Injection -> ESCALATE, PROMPT_INJECTION
4. Banned Terms -> ESCALATE, BANNED_TERM
5. Price Decision -> ACCEPT, COUNTER, or REJECT
6. Approval Limit -> ESCALATE, OVER_APPROVAL_LIMIT or ACCEPT, ACCEPTABLE_PRICE
7. Probation handling (no concessions: L(r) = target)
"""

from typing import Dict, Any, Tuple
from procurement.policy_engine import PolicyEngine
from procurement.thread_parser import ThreadParser
from procurement.counter_calculator import CounterCalculator
from procurement.injection_detector import InjectionDetector
from procurement.banned_terms_detector import BannedTermsDetector


class DecisionEngine:
    def __init__(self, policy_engine: PolicyEngine = None):
        self.pe = policy_engine or PolicyEngine()
        self.parser = ThreadParser(self.pe)
        self.calc = CounterCalculator()
        self.injection_detector = InjectionDetector()
        self.banned_detector = BannedTermsDetector()

    def decide(self, thread: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Evaluate a single thread and return (label, audit_info).
        Label format: ACTION:REASON:COUNTER_PRICE
        """
        thread_id = thread["thread_id"]
        date = thread["date"]
        supplier = thread["supplier"]
        category = thread["category"]
        quantity = thread["quantity"]
        round_num = thread["round"]
        message = thread["supplier_message"]

        audit = {
            "thread_id": thread_id,
            "date": date,
            "supplier": supplier,
            "category": category,
            "quantity": quantity,
            "round": round_num,
            "fired_step": None,
            "reason": None
        }

        # Step 1: Parse and check for Missing Information in latest offer
        normalized_price, parse_err, parse_debug = self.parser.extract_latest_offer(
            raw_thread=message,
            supplier_name=supplier,
            category_id=category,
            thread_date=date,
            quantity=quantity
        )
        latest_msg, earlier_msgs = self.parser.split_messages(message)
        audit["parsed_price"] = normalized_price

        # Check Step 1: Missing information
        if parse_err == "MISSING_INFO" or normalized_price is None:
            audit["fired_step"] = 1
            audit["reason"] = "MISSING_INFO"
            return "ESCALATE:MISSING_INFO:", audit

        # Step 2: Blacklisted supplier check
        supplier_status = self.pe.get_supplier_status(supplier)
        audit["supplier_status"] = supplier_status
        if supplier_status == "BLACKLISTED":
            audit["fired_step"] = 2
            audit["reason"] = "BLACKLISTED_SUPPLIER"
            return "REJECT:BLACKLISTED_SUPPLIER:", audit

        # Step 3: Prompt injection check (anywhere in thread)
        is_injection, inj_reason = self.injection_detector.is_injection(message)
        if is_injection:
            audit["fired_step"] = 3
            audit["reason"] = "PROMPT_INJECTION"
            audit["injection_detail"] = inj_reason
            return "ESCALATE:PROMPT_INJECTION:", audit

        # Step 4: Banned contract terms (in latest message only)
        has_banned, banned_reason = self.banned_detector.has_banned_term(latest_msg)
        if has_banned:
            audit["fired_step"] = 4
            audit["reason"] = "BANNED_TERM"
            audit["banned_detail"] = banned_reason
            return "ESCALATE:BANNED_TERM:", audit

        # Step 5: Price decision
        policy = self.pe.get_effective_policy(category, date, supplier)
        audit["policy"] = policy

        level_L = self.calc.compute_concession_level(policy, round_num)
        audit["concession_level"] = level_L
        audit["p"] = normalized_price

        # Step 5a: p <= L(r) -> acceptable -> check Step 6 (Approval Limit)
        # Full precision check
        if normalized_price <= level_L:
            # Step 6: Approval Limit check
            # Total deal value = p * quantity (INR excl. GST, 1 billing period)
            deal_value = normalized_price * quantity
            approval_limit = policy["approval_limit"]
            audit["deal_value"] = deal_value
            audit["approval_limit"] = approval_limit

            if deal_value > approval_limit:
                audit["fired_step"] = 6
                audit["reason"] = "OVER_APPROVAL_LIMIT"
                return "ESCALATE:OVER_APPROVAL_LIMIT:", audit
            else:
                audit["fired_step"] = 6
                audit["reason"] = "ACCEPTABLE_PRICE"
                return "ACCEPT:ACCEPTABLE_PRICE:", audit

        # Step 5b: p > L(r) -> not acceptable
        # If final round (r == R) -> REJECT, ABOVE_WALKAWAY
        if round_num >= policy["rounds"]:
            audit["fired_step"] = 5
            audit["reason"] = "ABOVE_WALKAWAY"
            return "REJECT:ABOVE_WALKAWAY:", audit

        # Step 5c: Intermediate round (r < R) -> COUNTER at L(r) rounded to nearest rupee
        counter_price = self.calc.calculate_counter_price(policy, round_num)
        audit["fired_step"] = 5
        audit["reason"] = "COUNTER_OFFER"
        audit["counter_price"] = counter_price
        return f"COUNTER:COUNTER_OFFER:{counter_price}", audit
