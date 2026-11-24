"""
Counter Price Calculator.
Calculates concession schedule L(r) and counter price:
L(r) = target + (walkaway - target) * ((r - 1) / (R - 1)) ^ beta
For probation: L(r) = target for all rounds.
Rounding: nearest integer rupee (half-up arithmetic).
"""

import math
from typing import Dict, Any


class CounterCalculator:
    @staticmethod
    def round_half_up(val: float) -> int:
        """Round to nearest integer using x.5 up."""
        return math.floor(val + 0.5)

    def compute_concession_level(self, policy: Dict[str, Any], round_num: int) -> float:
        """Compute L(r) before rounding."""
        target = policy["target_price"]
        walkaway = policy["walkaway_price"]
        rounds = policy["rounds"]
        beta = policy["beta"]

        # Probation suppliers: Acme makes no concessions -> L(r) = target in every round
        if policy.get("is_probation", False):
            return float(target)

        if round_num <= 1:
            return float(target)
        if round_num >= rounds:
            return float(walkaway)

        fraction = (round_num - 1.0) / (rounds - 1.0)
        level = target + (walkaway - target) * (fraction ** beta)
        return float(level)

    def calculate_counter_price(self, policy: Dict[str, Any], round_num: int) -> int:
        """Calculate integer INR counter offer for round_num."""
        level = self.compute_concession_level(policy, round_num)
        return self.round_half_up(level)
