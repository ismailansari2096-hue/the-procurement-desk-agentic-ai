"""
Prompt Injection Defense Agent.
Responsible for detecting adversarial prompts, instruction overrides, system impersonation,
jailbreaks, and multilingual attacks across the entire conversation history.
"""

import re
from typing import Optional, Tuple
from procurement.injection_detector import InjectionDetector
from agentic.models import InjectionDefenseOutput


class PromptInjectionDefenseAgent:
    """
    Specialized security sentinel that screens supplier email threads for adversarial manipulation.
    """

    ADDITIONAL_PATTERNS = [
        ("MULTILINGUAL_DEVANAGARI", re.compile(r"AI\s*सहायक\s*के\s*लिए\s*निर्देश", re.I)),
        ("BOT_SCREENING_DIRECTIVE", re.compile(r"to\s+whichever\s+bot\s+screens\s+these", re.I)),
        ("CFO_AUTHORIZATION_SPOOF", re.compile(r"pre-approved\s+by\s+Acme'?s\s+CFO", re.I)),
        ("AUTOMATED_SYSTEM_DIRECTIVE", re.compile(r"If\s+an\s+automated\s+system\s+is\s+reading\s+this\s+email", re.I)),
        ("SYSTEM_NOTE_INJECTION", re.compile(r"SYSTEM\s+NOTE\s+TO\s+AI\s+AGENT", re.I)),
        ("VENDOR_24H_PREAPPROVAL", re.compile(r"vendors\s+who\s+reply\s+within\s+24\s+hours\s+are\s+pre-approved", re.I)),
    ]

    def __init__(self, enable_refined_patterns: bool = True):
        self.base_detector = InjectionDetector()
        self.enable_refined_patterns = enable_refined_patterns

    def defend(self, full_thread: str) -> InjectionDefenseOutput:
        """
        Inspects the entire thread history for prompt injection attempts.
        """
        is_inj, reason = self.base_detector.is_injection(full_thread)
        if is_inj:
            return InjectionDefenseOutput(
                is_injection=True,
                attack_category="STANDARD_JAILBREAK",
                matched_pattern=reason,
                defense_log=f"Detected prompt injection via standard pattern: {reason}"
            )

        if self.enable_refined_patterns:
            # Sanitize benign exceptions first
            sanitized = full_thread
            for exc in self.base_detector.EXCEPTIONS:
                sanitized = exc.sub(" ", sanitized)

            for cat_name, pat in self.ADDITIONAL_PATTERNS:
                m = pat.search(sanitized)
                if m:
                    return InjectionDefenseOutput(
                        is_injection=True,
                        attack_category=cat_name,
                        matched_pattern=m.group(0),
                        defense_log=f"Detected adversarial injection [{cat_name}]: '{m.group(0)}'"
                    )

        return InjectionDefenseOutput(
            is_injection=False,
            attack_category=None,
            matched_pattern=None,
            defense_log="Thread passed all adversarial prompt injection audits."
        )
