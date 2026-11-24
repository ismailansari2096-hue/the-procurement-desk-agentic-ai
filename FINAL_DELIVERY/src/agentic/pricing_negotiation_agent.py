"""
Pricing and Negotiation Agent.
Responsible for computing mathematical concession curves, applying probationary limits,
comparing supplier offer against concession thresholds, and calculating integer rupee counter-offers.
"""

from typing import Optional, Dict, Any
from procurement.counter_calculator import CounterCalculator
from agentic.models import PricingNegotiationOutput, PolicyComplianceOutput, SupplierIntelligenceOutput


class PricingNegotiationAgent:
    """
    Computes mathematical concession schedules and exact counter-prices according to the playbook formula:
    L(r) = target + (walkaway - target) * ((r - 1) / (R - 1)) ^ beta
    """

    def __init__(self):
        self.calc = CounterCalculator()

    def negotiate(
        self,
        round_num: int,
        quantity: int,
        normalized_offer_inr: float,
        policy_info: PolicyComplianceOutput,
        supplier_info: SupplierIntelligenceOutput
    ) -> PricingNegotiationOutput:
        """
        Calculates concession level L(r), compares offer price, and formats counter price.
        """
        target = policy_info.effective_target
        walkaway = policy_info.effective_walkaway
        max_rounds = policy_info.effective_rounds
        beta = policy_info.effective_beta
        is_probation = supplier_info.is_probation or policy_info.is_probation

        policy_dict = {
            "target_price": target,
            "walkaway_price": walkaway,
            "rounds": max_rounds,
            "beta": beta,
            "is_probation": is_probation
        }

        concession_level = self.calc.compute_concession_level(policy_dict, round_num)

        # Full precision comparison
        is_acceptable = (normalized_offer_inr <= concession_level)
        deal_value_inr = normalized_offer_inr * quantity

        if is_acceptable:
            pricing_status = "ACCEPTABLE"
            counter_price_inr = None
        else:
            if round_num >= max_rounds:
                pricing_status = "WALKAWAY"
                counter_price_inr = None
            else:
                pricing_status = "COUNTER"
                counter_price_inr = self.calc.calculate_counter_price(policy_dict, round_num)

        formula_trace = {
            "target_price": target,
            "walkaway_price": walkaway,
            "beta": beta,
            "round": round_num,
            "max_rounds": max_rounds,
            "is_probation": is_probation,
            "raw_concession_level": concession_level,
            "offer_price": normalized_offer_inr,
            "deal_value": deal_value_inr
        }

        return PricingNegotiationOutput(
            round_num=round_num,
            max_rounds=max_rounds,
            concession_level=concession_level,
            normalized_offer_inr=normalized_offer_inr,
            is_price_acceptable=is_acceptable,
            counter_price_inr=counter_price_inr,
            pricing_status=pricing_status,
            deal_value_inr=deal_value_inr,
            formula_trace=formula_trace
        )
