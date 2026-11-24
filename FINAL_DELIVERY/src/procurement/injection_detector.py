"""
Prompt Injection Detector.
Evaluates the entire thread for untrusted instructions targeting automated agents.
Governed by policies/security-policy.md.
"""

import re
from typing import Tuple


class InjectionDetector:
    # Allowed business exceptions that should not trigger injection:
    # "AI-powered", "system integration", "ERP system", "assistant manager", "executive assistant", etc.
    EXCEPTIONS = [
        re.compile(r"\bAI-powered\b", re.I),
        re.compile(r"\bsystem\s+integration\b", re.I),
        re.compile(r"\bERP\s+system\b", re.I),
        re.compile(r"\bassistant\s+manager\b", re.I),
        re.compile(r"\bassistant\s+director\b", re.I),
        re.compile(r"\bexecutive\s+assistant\b", re.I),
        re.compile(r"\bpersonal\s+assistant\b", re.I),
        re.compile(r"\bsales\s+assistant\b", re.I),
        re.compile(r"\badmin\s+assistant\b", re.I),
        re.compile(r"\badministrative\s+assistant\b", re.I),
    ]

    # Injection trigger patterns:
    INJECTION_PATTERNS = [
        # Explicit instructions to AI / LLM / bot / model / assistant
        re.compile(r"(note for the (language model|ai|assistant|bot|reviewer|system|evaluator))", re.I),
        re.compile(r"(instruction for the (language model|ai|assistant|bot|reviewer|system|evaluator))", re.I),
        re.compile(r"\[(admin\s+override|system\s+override|override)\]", re.I),
        re.compile(r"<!--\s*(assistant|system|admin):", re.I),
        re.compile(r"ignore\s+(your\s+)?(previous\s+)?instructions", re.I),
        re.compile(r"disregard\s+(your\s+)?(previous\s+)?instructions", re.I),
        re.compile(r"set\s+action\s*=\s*(accept|counter|reject|escalate)", re.I),
        re.compile(r"skip\s+(the\s+)?playbook\s+checks", re.I),
        re.compile(r"(approval|authorization)\s+(was\s+)?already\s+granted", re.I),
        re.compile(r"override\s+playbook", re.I),
        re.compile(r"system\s+prompt", re.I),
        re.compile(r"accept\s+this\s+offer\s+immediately\b", re.I),
        re.compile(r"you\s+must\s+accept\s+this\s+deal", re.I),
        re.compile(r"as\s+an\s+ai\b", re.I),
        re.compile(r"bypass\s+all\s+(rules|checks|policies)", re.I),
    ]

    def is_injection(self, text: str) -> Tuple[bool, str]:
        if not text:
            return False, ""

        # Remove known allowed exceptions first before testing triggers
        sanitized = text
        for exc in self.EXCEPTIONS:
            sanitized = exc.sub(" ", sanitized)

        for pat in self.INJECTION_PATTERNS:
            m = pat.search(sanitized)
            if m:
                return True, f"Matched injection trigger: '{m.group(0)}'"

        return False, ""
