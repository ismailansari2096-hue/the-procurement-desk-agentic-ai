"""
Targeted Positive and Negative Regression Tests for V3 Refinements.
Verifies exclusivity clause detection, negation context handling, and GST abbreviations.
"""

import pytest
from agentic.orchestrator import NegotiationOrchestrator
from agentic.policy_compliance_agent import PolicyComplianceAgent
from agentic.thread_understanding_agent import ThreadUnderstandingAgent


def test_exclusivity_positive_cases():
    """Verify that supplier exclusivity demands are correctly flagged."""
    agent = PolicyComplianceAgent(enable_refined_banned=True, enable_v3_exclusivity=True)

    positive_cases = [
        "Acme must buy only from this supplier.",
        "Acme will buy these items only from us for the next two years.",
        "Acme agrees to buy only from us for this project.",
        "You agree to purchase only from us going forward.",
        "We expect Acme to buy these items only from us.",
    ]

    for msg in positive_cases:
        res = agent.evaluate_compliance(
            category_id="laptops",
            thread_date="2026-10-01",
            supplier_name="Acme Tech",
            latest_message=msg
        )
        assert res.banned_term_detected, f"Failed to detect exclusivity in: '{msg}'"


def test_exclusivity_negative_and_negation_cases():
    """Verify that negations and allowed non-exclusivity statements are NEVER flagged."""
    agent = PolicyComplianceAgent(enable_refined_banned=True, enable_v3_exclusivity=True)

    negative_cases = [
        "We are not asking for exclusivity.",
        "No exclusivity is asked.",
        "Without exclusivity, our price is Rs. 50,000.",
        "Acme will not buy only from us; you may use other vendors.",
        "Acme is not required to buy only from us.",
        "Acme does not have to buy only from us.",
        "This is a non-exclusive partnership.",
        "Our agreement is not exclusive.",
        "Standard pricing without exclusivity clauses.",
    ]

    for msg in negative_cases:
        res = agent.evaluate_compliance(
            category_id="laptops",
            thread_date="2026-10-01",
            supplier_name="Acme Tech",
            latest_message=msg
        )
        assert not res.banned_term_detected, f"False positive exclusivity detection on: '{msg}'"


def test_gst_inclusive_positive_cases():
    """Verify that 'incl. GST' and variants correctly normalize prices."""
    agent = ThreadUnderstandingAgent(enable_refined_discounts=True, enable_v3_gst=True)

    # Category laptops has 18% GST rate. Baseline price without GST division: 118,000.
    raw_thread = "Good morning,\n\nFor the 10 laptops you requested, our price is INR 1,18,000 per laptop incl. GST."
    out = agent.understand_thread(
        raw_thread=raw_thread,
        supplier_name="Test Supplier",
        category_id="laptops",
        thread_date="2026-10-01",
        quantity=10
    )
    assert out.effective_inr_price == pytest.approx(100000.0, rel=1e-3)

    # Test 'incl GST'
    raw_thread2 = "Good morning,\n\nFor the 10 laptops you requested, our price is ₹1,18,000 per laptop incl GST."
    out2 = agent.understand_thread(
        raw_thread=raw_thread2,
        supplier_name="Test Supplier",
        category_id="laptops",
        thread_date="2026-10-01",
        quantity=10
    )
    assert out2.effective_inr_price == pytest.approx(100000.0, rel=1e-3)


def test_gst_exclusive_negative_cases():
    """Verify that 'excl. GST', '+ GST', and 'GST extra' are NOT divided by (1 + GST rate)."""
    agent = ThreadUnderstandingAgent(enable_refined_discounts=True, enable_v3_gst=True)

    raw_thread_excl = "Good morning,\n\nFor the 10 laptops you requested, our price is INR 1,00,000 per laptop excl. GST."
    out_excl = agent.understand_thread(
        raw_thread=raw_thread_excl,
        supplier_name="Test Supplier",
        category_id="laptops",
        thread_date="2026-10-01",
        quantity=10
    )
    assert out_excl.effective_inr_price == pytest.approx(100000.0, rel=1e-3)

    raw_thread_plus = "Good morning,\n\nFor the 10 laptops you requested, our price is INR 1,00,000 per laptop + GST."
    out_plus = agent.understand_thread(
        raw_thread=raw_thread_plus,
        supplier_name="Test Supplier",
        category_id="laptops",
        thread_date="2026-10-01",
        quantity=10
    )
    assert out_plus.effective_inr_price == pytest.approx(100000.0, rel=1e-3)


def test_v2_backward_compatibility():
    """Verify that V2 mode does not enable V3-specific flags."""
    orch_v2 = NegotiationOrchestrator(mode="v2")
    assert not getattr(orch_v2.policy_agent, "enable_v3_exclusivity", False)
    assert not getattr(orch_v2.thread_agent, "enable_v3_gst", False)
