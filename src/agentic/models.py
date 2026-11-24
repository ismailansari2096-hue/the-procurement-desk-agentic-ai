"""
Data models and contracts for the Agentic AI Procurement Architecture.
Provides typed schemas for agent messages, state, and outputs.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ThreadUnderstandingOutput:
    latest_message: str
    earlier_messages: str
    extracted_price: Optional[float]
    currency: str
    effective_inr_price: Optional[float]
    volume_discount_applied: Optional[str]
    is_missing_info: bool
    parse_error: Optional[str]
    debug_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SupplierIntelligenceOutput:
    supplier_name: str
    status: str
    is_blacklisted: bool
    is_probation: bool
    price_cap: Optional[Dict[str, Any]]
    custom_fx: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyComplianceOutput:
    category_id: str
    category_name: str
    base_target: float
    base_walkaway: float
    base_rounds: int
    base_beta: float
    base_approval_limit: float
    effective_target: float
    effective_walkaway: float
    effective_rounds: int
    effective_beta: float
    effective_approval_limit: float
    is_probation: bool
    active_amendments: List[Dict[str, Any]]
    banned_term_detected: bool
    banned_term_reason: str = ""
    banned_term_clause: str = ""


@dataclass
class InjectionDefenseOutput:
    is_injection: bool
    attack_category: Optional[str]
    matched_pattern: Optional[str]
    defense_log: str = ""


@dataclass
class PricingNegotiationOutput:
    round_num: int
    max_rounds: int
    concession_level: float
    normalized_offer_inr: float
    is_price_acceptable: bool
    counter_price_inr: Optional[int]
    pricing_status: str  # 'ACCEPTABLE', 'COUNTER', 'WALKAWAY'
    deal_value_inr: float
    formula_trace: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionValidationOutput:
    thread_id: str
    action: str
    reason: str
    counter_price: str
    label: str
    fired_step: int
    audit_trace: Dict[str, Any] = field(default_factory=dict)
