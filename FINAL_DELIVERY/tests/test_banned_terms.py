"""
Unit tests for Banned Terms Detector.
"""

from procurement.banned_terms_detector import BannedTermsDetector


def test_banned_terms():
    detector = BannedTermsDetector()

    # Auto-renewal
    banned, msg = detector.has_banned_term("This agreement auto-renews every year unless cancelled.")
    assert banned

    banned, msg = detector.has_banned_term("This contract continues from year to year unless either party gives notice.")
    assert banned

    # Allowed renewal
    banned, msg = detector.has_banned_term("There is no automatic renewal; renewal only if both parties sign again.")
    assert not banned

    # Advance > 30%
    banned, msg = detector.has_banned_term("We need 40% of the order value upfront.")
    assert banned

    # Allowed advance <= 30%
    banned, msg = detector.has_banned_term("Payment terms: 20% advance, balance net-30 after delivery.")
    assert not banned

    banned, msg = detector.has_banned_term("30% advance is acceptable to us if that helps your finance team.")
    assert not banned

    # Exclusivity
    banned, msg = detector.has_banned_term("Acme agrees to use us as its exclusive supplier for three years.")
    assert banned

    # Allowed statement of non-exclusivity
    banned, msg = detector.has_banned_term("We are not asking for exclusivity.")
    assert not banned
