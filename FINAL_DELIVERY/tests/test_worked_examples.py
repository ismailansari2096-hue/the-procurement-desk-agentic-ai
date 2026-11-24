"""
Regression test suite asserting 100% exact-match accuracy
across all 40 competition worked examples.
"""

import pytest
from pathlib import Path
from procurement.data_loader import load_threads, load_sample_answers
from procurement.decision_engine import DecisionEngine
from procurement.config import RAW_DATA_DIR


@pytest.fixture(scope="module")
def decision_engine():
    return DecisionEngine()


@pytest.fixture(scope="module")
def sample_data():
    threads = load_threads(RAW_DATA_DIR / "sample_threads.csv")
    answers = load_sample_answers(RAW_DATA_DIR / "sample_answers.csv")
    return threads, answers


def test_worked_examples_perfect_accuracy(decision_engine, sample_data):
    threads, answers = sample_data
    assert len(threads) == 40
    assert len(answers) == 40

    failures = []
    for thread in threads:
        tid = thread["thread_id"]
        expected_label = answers[tid]
        actual_label, audit = decision_engine.decide(thread)

        if actual_label != expected_label:
            failures.append(f"{tid}: Expected '{expected_label}', Got '{actual_label}' (Step {audit.get('fired_step')})")

    assert not failures, f"Mismatches on worked examples:\n" + "\n".join(failures)
