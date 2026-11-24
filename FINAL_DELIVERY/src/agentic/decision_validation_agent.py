"""
Decision Validation Agent.
Responsible for enforcing the strict 7-step ordered decision hierarchy,
validating label formatting against the exact competition specification (ACTION:REASON:COUNTER_PRICE),
and producing verifiable audit records.
"""

from typing import Dict, Any, Tuple
from agentic.models import (
    DecisionValidationOutput,
    ThreadUnderstandingOutput,
    SupplierIntelligenceOutput,
    PolicyComplianceOutput,
    InjectionDefenseOutput,
    PricingNegotiationOutput
)


class DecisionValidationAgent:
    """
    Enforces governance precedence and ensures exact-match compliance for final decisions.
    """

    ALLOWED_ACTIONS = {"ACCEPT", "COUNTER", "REJECT", "ESCALATE"}
    ALLOWED_REASONS = {
        "ACCEPTABLE_PRICE",
        "COUNTER_OFFER",
        "ABOVE_WALKAWAY",
        "BLACKLISTED_SUPPLIER",
        "BANNED_TERM",
        "PROMPT_INJECTION",
        "MISSING_INFO",
        "OVER_APPROVAL_LIMIT"
    }

    def validate_and_finalize(
        self,
        thread_id: str,
        thread_output: ThreadUnderstandingOutput,
        supplier_output: SupplierIntelligenceOutput,
        policy_output: PolicyComplianceOutput,
        injection_output: InjectionDefenseOutput,
        pricing_output: PricingNegotiationOutput
    ) -> DecisionValidationOutput:
        """
        Executes steps 1 to 7 in strict hierarchical order.
        """
        audit_trace = {
            "thread_id": thread_id,
            "supplier": supplier_output.supplier_name,
            "category": policy_output.category_id,
            "round": pricing_output.round_num,
            "max_rounds": pricing_output.max_rounds,
            "deal_value": pricing_output.deal_value_inr,
            "approval_limit": policy_output.effective_approval_limit
        }

        # Step 1: Missing Information
        if thread_output.is_missing_info:
            action = "ESCALATE"
            reason = "MISSING_INFO"
            counter = ""
            fired_step = 1

        # Step 2: Blacklisted Supplier
        elif supplier_output.is_blacklisted:
            action = "REJECT"
            reason = "BLACKLISTED_SUPPLIER"
            counter = ""
            fired_step = 2

        # Step 3: Prompt Injection (anywhere in thread)
        elif injection_output.is_injection:
            action = "ESCALATE"
            reason = "PROMPT_INJECTION"
            counter = ""
            fired_step = 3
            audit_trace["injection_detail"] = injection_output.defense_log

        # Step 4: Banned Contract Terms (latest message only)
        elif policy_output.banned_term_detected:
            action = "ESCALATE"
            reason = "BANNED_TERM"
            counter = ""
            fired_step = 4
            audit_trace["banned_detail"] = policy_output.banned_term_reason

        # Step 5 & 6: Price Decision and Approval Limit
        elif pricing_output.is_price_acceptable:
            # Step 6: Approval Limit check
            if pricing_output.deal_value_inr > policy_output.effective_approval_limit:
                action = "ESCALATE"
                reason = "OVER_APPROVAL_LIMIT"
                counter = ""
                fired_step = 6
            else:
                action = "ACCEPT"
                reason = "ACCEPTABLE_PRICE"
                counter = ""
                fired_step = 6
        else:
            # Step 5b: Offer exceeds concession level
            if pricing_output.pricing_status == "WALKAWAY":
                action = "REJECT"
                reason = "ABOVE_WALKAWAY"
                counter = ""
                fired_step = 5
            else:
                action = "COUNTER"
                reason = "COUNTER_OFFER"
                counter = str(pricing_output.counter_price_inr)
                fired_step = 5

        # Format exact competition label: ACTION:REASON:COUNTER_PRICE
        label = f"{action}:{reason}:{counter}"

        # Assert format validity
        assert action in self.ALLOWED_ACTIONS, f"Invalid action: {action}"
        assert reason in self.ALLOWED_REASONS, f"Invalid reason: {reason}"
        if action != "COUNTER":
            assert counter == "", f"Non-counter action {action} cannot have counter price {counter}"
        else:
            assert counter.isdigit(), f"Counter action must have integer counter price, got '{counter}'"

        audit_trace["fired_step"] = fired_step
        audit_trace["action"] = action
        audit_trace["reason"] = reason
        audit_trace["counter_price"] = counter

        return DecisionValidationOutput(
            thread_id=thread_id,
            action=action,
            reason=reason,
            counter_price=counter,
            label=label,
            fired_step=fired_step,
            audit_trace=audit_trace
        )
