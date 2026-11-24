"""
Unit tests for CounterCalculator and Concession Formulas.
"""

import pytest
from procurement.counter_calculator import CounterCalculator


def test_concession_schedule():
    calc = CounterCalculator()
    policy = {
        "target_price": 62000,
        "walkaway_price": 70000,
        "rounds": 4,
        "beta": 2.0,
        "is_probation": False
    }

    # Round 1: L(1) = target = 62000
    assert calc.calculate_counter_price(policy, 1) == 62000

    # Round 2: 62000 + 8000 * (1/3)^2 = 62888.888... -> 62889
    assert calc.calculate_counter_price(policy, 2) == 62889

    # Round 3: 62000 + 8000 * (2/3)^2 = 62000 + 8000 * (4/9) = 65555.555... -> 65556
    assert calc.calculate_counter_price(policy, 3) == 65556

    # Round 4: L(4) = walkaway = 70000
    assert calc.calculate_counter_price(policy, 4) == 70000


def test_probation_concession():
    calc = CounterCalculator()
    policy = {
        "target_price": 18000,
        "walkaway_price": 22000,
        "rounds": 4,
        "beta": 2.0,
        "is_probation": True
    }
    # For probation, L(r) = target for all rounds
    assert calc.calculate_counter_price(policy, 1) == 18000
    assert calc.calculate_counter_price(policy, 2) == 18000
    assert calc.calculate_counter_price(policy, 3) == 18000
    assert calc.calculate_counter_price(policy, 4) == 18000
