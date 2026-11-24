"""
Negotiation Orchestrator.
Coordinates the 6 specialized agents, maintains the communication blackboard,
and executes end-to-end negotiation analysis with full explainability.
"""

from typing import Dict, Any, Tuple, Optional
from procurement.policy_engine import PolicyEngine
from agentic.models import (
    DecisionValidationOutput,
    ThreadUnderstandingOutput,
    SupplierIntelligenceOutput,
    PolicyComplianceOutput,
    InjectionDefenseOutput,
    PricingNegotiationOutput
)
from agentic.thread_understanding_agent import ThreadUnderstandingAgent
from agentic.supplier_intelligence_agent import SupplierIntelligenceAgent
from agentic.policy_compliance_agent import PolicyComplianceAgent
from agentic.injection_defense_agent import PromptInjectionDefenseAgent
from agentic.pricing_negotiation_agent import PricingNegotiationAgent
from agentic.decision_validation_agent import DecisionValidationAgent


class NegotiationOrchestrator:
    """
    Multi-Agent Coordination Blackboard for Autonomous Supplier Negotiation.
    """

    def __init__(self, mode: str = "v2", policy_engine: Optional[PolicyEngine] = None):
        """
        mode: 'v1' for baseline logic (public score 0.90375),
              'v2' for refined competitive logic (public score 0.97063),
              'v3' for candidate with exclusivity & GST refinements (public score 0.98205),
              'v4' for forensic candidate with word-based numerical parsing correction.
        """
        self.mode = mode.lower()
        self.pe = policy_engine or PolicyEngine()
        is_v2_or_v3_or_v4 = self.mode in ("v2", "v3", "v4")
        is_v3_or_v4 = self.mode in ("v3", "v4")
        is_v4 = (self.mode == "v4")

        # Initialize the 6 logical agents
        self.thread_agent = ThreadUnderstandingAgent(
            self.pe,
            enable_refined_discounts=is_v2_or_v3_or_v4,
            enable_v3_gst=is_v3_or_v4,
            enable_v4_word_pricing=is_v4
        )
        self.supplier_agent = SupplierIntelligenceAgent(self.pe)
        self.policy_agent = PolicyComplianceAgent(
            self.pe,
            enable_refined_banned=is_v2_or_v3_or_v4,
            enable_v3_exclusivity=is_v3_or_v4
        )
        self.injection_agent = PromptInjectionDefenseAgent(enable_refined_patterns=is_v2_or_v3_or_v4)
        self.pricing_agent = PricingNegotiationAgent()
        self.validation_agent = DecisionValidationAgent()

    def process_thread(self, thread: Dict[str, Any]) -> Tuple[DecisionValidationOutput, Dict[str, Any]]:
        """
        Coordinates all agents through the negotiation analysis workflow.
        Returns (DecisionValidationOutput, full_blackboard_trace).
        """
        thread_id = str(thread["thread_id"])
        date = str(thread["date"])
        supplier = str(thread["supplier"])
        category = str(thread["category"])
        quantity = int(thread["quantity"])
        round_num = int(thread["round"])
        message = str(thread["supplier_message"])

        # Agent 1: Thread Understanding
        thread_out = self.thread_agent.understand_thread(
            raw_thread=message,
            supplier_name=supplier,
            category_id=category,
            thread_date=date,
            quantity=quantity
        )

        # Agent 2: Supplier Intelligence
        supplier_out = self.supplier_agent.inspect_supplier(supplier)

        # Agent 3: Policy Compliance
        policy_out = self.policy_agent.evaluate_compliance(
            category_id=category,
            thread_date=date,
            supplier_name=supplier,
            latest_message=thread_out.latest_message
        )

        # Agent 4: Prompt Injection Defense
        injection_out = self.injection_agent.defend(message)

        # Agent 5: Pricing and Negotiation
        effective_offer_inr = thread_out.effective_inr_price if thread_out.effective_inr_price is not None else 0.0
        pricing_out = self.pricing_agent.negotiate(
            round_num=round_num,
            quantity=quantity,
            normalized_offer_inr=effective_offer_inr,
            policy_info=policy_out,
            supplier_info=supplier_out
        )

        # Agent 6: Decision Validation
        decision_out = self.validation_agent.validate_and_finalize(
            thread_id=thread_id,
            thread_output=thread_out,
            supplier_output=supplier_out,
            policy_output=policy_out,
            injection_output=injection_out,
            pricing_output=pricing_out
        )

        # Comprehensive blackboard trace
        blackboard = {
            "mode": self.mode,
            "thread_understanding": thread_out,
            "supplier_intelligence": supplier_out,
            "policy_compliance": policy_out,
            "injection_defense": injection_out,
            "pricing_negotiation": pricing_out,
            "decision_validation": decision_out
        }

        return decision_out, blackboard

    def decide(self, thread: Dict[str, Any]) -> str:
        """
        Fast execution returning the exact competition label.
        """
        decision_out, _ = self.process_thread(thread)
        return decision_out.label
