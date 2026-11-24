"""
Unit tests for Policy Engine, Amendments, and Supplier Contracts.
"""

import pytest
from procurement.policy_engine import PolicyEngine


@pytest.fixture(scope="module")
def pe():
    return PolicyEngine()


def test_base_category_loading(pe):
    policy = pe.get_effective_policy("laptops", "2026-09-01", "Coastline Caterers")
    assert policy["target_price"] == 62000
    assert policy["walkaway_price"] == 70000
    assert policy["rounds"] == 4
    assert policy["beta"] == 2.0
    assert policy["approval_limit"] == 4000000


def test_dated_amendments(pe):
    # AMD-01: Courier walk-away is 210 from 2026-09-22 (was 200)
    before = pe.get_effective_policy("courier", "2026-09-21", "Redwood Couriers")
    assert before["walkaway_price"] == 200

    after = pe.get_effective_policy("courier", "2026-09-22", "Redwood Couriers")
    assert after["walkaway_price"] == 210

    # AMD-08 (2026-12-04: walk-away 2330) vs AMD-07 (2026-12-05: walk-away 2360)
    pol_03 = pe.get_effective_policy("led-lighting", "2026-12-03", "Everbright Lighting")
    assert pol_03["walkaway_price"] == 2200

    pol_04 = pe.get_effective_policy("led-lighting", "2026-12-04", "Everbright Lighting")
    assert pol_04["walkaway_price"] == 2330

    pol_05 = pe.get_effective_policy("led-lighting", "2026-12-05", "Everbright Lighting")
    assert pol_05["walkaway_price"] == 2360


def test_supplier_contract_overrides(pe):
    # Helix CRM has price cap for Catering of 400
    pol = pe.get_effective_policy("catering", "2026-10-01", "Helix CRM")
    assert pol["walkaway_price"] == 400

    # Aster Cleaning has custom USD rate of 84.0
    assert pe.get_exchange_rate("USD", "Aster Cleaning Co") == 84.0
    assert pe.get_exchange_rate("USD", "Coastline Caterers") == 84.5


def test_supplier_status(pe):
    assert pe.get_supplier_status("GreenLeaf Facility Care") == "BLACKLISTED"
    assert pe.get_supplier_status("Lumen Workspace") == "BLACKLISTED"
    assert pe.get_supplier_status("Orbit Electronics") == "BLACKLISTED"
    assert pe.get_supplier_status("Banyan Guarding") == "PROBATION"
    assert pe.get_supplier_status("Bluepeak Technologies") == "Approved"
