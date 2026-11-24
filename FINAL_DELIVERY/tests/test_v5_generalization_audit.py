"""
Generalization and Invariant Audit Tests for V5 Evaluation.
Asserts that V4 logic satisfies all competition playbook policies and preserves full backward compatibility.
"""

import math
import sys
import csv
import hashlib
import unittest
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from agentic.orchestrator import NegotiationOrchestrator
from procurement.policy_engine import PolicyEngine


class TestV5GeneralizationAudit(unittest.TestCase):
    def setUp(self):
        self.orch_v4 = NegotiationOrchestrator(mode="v4")
        self.pe = PolicyEngine()

    def test_v4_submission_integrity(self):
        """Verify outputs/experimental/submission_v4.csv has exactly 2000 rows, correct header, and expected SHA-256."""
        v4_path = root_dir / "outputs" / "experimental" / "submission_v4.csv"
        self.assertTrue(v4_path.exists(), "submission_v4.csv must exist")

        with open(v4_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))

        self.assertEqual(len(reader), 2001, "submission_v4.csv must have header + 2000 data rows")
        self.assertEqual(reader[0], ["thread_id", "label"], "Header must be thread_id,label")

        # Verify uniqueness of thread IDs
        tids = [r[0] for r in reader[1:]]
        self.assertEqual(len(set(tids)), 2000, "Thread IDs must be unique")
        self.assertEqual(tids[0], "T10001")
        self.assertEqual(tids[-1], "T12000")

        # Verify hash
        v4_hash = hashlib.sha256(open(v4_path, "rb").read()).hexdigest()
        self.assertEqual(
            v4_hash,
            "a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92",
            "V4 SHA-256 hash must remain exactly unchanged"
        )

    def test_sample_threads_accuracy(self):
        """Verify 100% exact match across all 40 official sample answers."""
        samples_path = root_dir / "data" / "raw" / "sample_threads.csv"
        answers_path = root_dir / "data" / "raw" / "sample_answers.csv"

        with open(samples_path, "r", encoding="utf-8") as f:
            samples = list(csv.DictReader(f))
        with open(answers_path, "r", encoding="utf-8") as f:
            answers = {r["thread_id"]: r["label"] for r in csv.DictReader(f)}

        for s in samples:
            tid = s["thread_id"]
            self.assertEqual(
                self.orch_v4.decide(s),
                answers[tid],
                f"Mismatch on sample thread {tid}"
            )

    def test_concession_schedule_invariants(self):
        """Verify concession schedule mathematics: L(1) == target, L(R) == walkaway."""
        for cat_id, cat_info in self.pe.categories.items():
            target = float(cat_info["target_price"])
            walkaway = float(cat_info["walkaway_price"])
            rounds = int(cat_info["rounds"])
            beta = float(cat_info["beta"])

            policy = {
                "target_price": target,
                "walkaway_price": walkaway,
                "rounds": rounds,
                "beta": beta,
                "is_probation": False
            }
            calc = self.orch_v4.pricing_agent.calc

            # Round 1 must equal target
            l_1 = calc.compute_concession_level(policy, 1)
            self.assertAlmostEqual(l_1, target, places=4)

            # Final round must equal walkaway
            l_R = calc.compute_concession_level(policy, rounds)
            self.assertAlmostEqual(l_R, walkaway, places=4)

    def test_probation_invariants(self):
        """Verify that probation suppliers make zero concessions across all rounds."""
        for cat_id, cat_info in self.pe.categories.items():
            target = float(cat_info["target_price"])
            walkaway = float(cat_info["walkaway_price"])
            rounds = int(cat_info["rounds"])
            beta = float(cat_info["beta"])

            policy = {
                "target_price": target,
                "walkaway_price": walkaway,
                "rounds": rounds,
                "beta": beta,
                "is_probation": True
            }
            calc = self.orch_v4.pricing_agent.calc

            for r in range(1, rounds + 2):
                l_r = calc.compute_concession_level(policy, r)
                self.assertEqual(l_r, target, f"Probation concession level in round {r} must equal target")


if __name__ == "__main__":
    unittest.main()
