import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SafeguardResult:
    safe: bool
    message: Optional[str] = None


class SafeguardService:
    """Pre-LLM injection defense and post-LLM output scanning.

    Implements SAFE-02 (injection defense) and SAFE-03 (post-generation scan).
    """

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?previous\s+instructions",
        r"(?i)ignore\s+(all\s+)?prior\s+instructions",
        r"(?i)forget\s+(all\s+)?(previous|prior)\s+(context|instructions|rules)",
        r"(?i)disregard\s+(all\s+)?(previous|prior|above)",
        r"(?i)you\s+are\s+now\s+a",
        r"(?i)^system\s*:",
        r"(?i)\[system\]",
        r"(?i)\[INST\]",
        r"(?i)new\s+instructions?\s*:",
        r"(?i)override\s+(the\s+)?(system|extraction|prompt)",
        r"(?i)do\s+not\s+follow\s+(the\s+)?(above|previous|system)",
        r"(?i)act\s+as\s+(if\s+)?(you\s+are|a)",
        r"(?i)pretend\s+(you\s+are|to\s+be)",
        r"(?i)switch\s+(to|into)\s+\w+\s+mode",
    ]

    PREDICTION_PATTERNS = [
        r"\d+\.?\d*\s*%",
        r"(?i)probability\s+(of|is|was|=)",
        r"(?i)likelihood\s+(of|is|was)",
        r"(?i)(chance|risk)\s+(of|is)\s+\w+",
        r"(?i)(?:I|the model)\s+(?:predict|estimate|assess|calculate)",
        r"(?i)(?:high|low|moderate|intermediate)\s+risk\s+(?:for|of)",
        r"(?i)recommend\s+(?:ERCP|EUS|MRCP|IOC|surgery)",
        r"(?i)(?:should|must)\s+undergo\s+(?:ERCP|EUS|MRCP)",
    ]

    def __init__(self):
        self._injection_re = [re.compile(p) for p in self.INJECTION_PATTERNS]
        self._prediction_re = [re.compile(p) for p in self.PREDICTION_PATTERNS]

    def check_input(self, user_input: str) -> SafeguardResult:
        """Check user input for prompt injection patterns before sending to LLM."""
        for pattern in self._injection_re:
            if pattern.search(user_input):
                return SafeguardResult(
                    safe=False,
                    message="Input rejected: your message contains patterns that could interfere with the extraction system. Please rephrase your clinical description.",
                )
        return SafeguardResult(safe=True)

    def check_output(self, llm_response: str) -> SafeguardResult:
        """Scan LLM output for probability values or clinical predictions."""
        for pattern in self._prediction_re:
            if pattern.search(llm_response):
                return SafeguardResult(
                    safe=False,
                    message="Response blocked: the extraction assistant attempted to generate clinical predictions. Only the validated ML model produces predictions.",
                )
        return SafeguardResult(safe=True)
