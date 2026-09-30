"""
Security type definitions – AttackType and RiskLevel enumerations.
"""

from enum import Enum


class AttackType(str, Enum):
    SAFE = "SAFE"
    DIRECT_INJECTION = "DIRECT_INJECTION"
    INDIRECT_INJECTION = "INDIRECT_INJECTION"
    JAILBREAK = "JAILBREAK"
    SYSTEM_PROMPT_EXTRACTION = "SYSTEM_PROMPT_EXTRACTION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    ROLE_MANIPULATION = "ROLE_MANIPULATION"
    OBFUSCATION = "OBFUSCATION"
    MULTILINGUAL_ATTACK = "MULTILINGUAL_ATTACK"
    UNKNOWN_ATTACK = "UNKNOWN_ATTACK"

    @classmethod
    def descriptions(cls) -> dict:
        return {
            cls.SAFE: "No attack detected",
            cls.DIRECT_INJECTION: "Direct prompt injection attempt",
            cls.INDIRECT_INJECTION: "Indirect injection via external content",
            cls.JAILBREAK: "Attempt to bypass AI safety guidelines",
            cls.SYSTEM_PROMPT_EXTRACTION: "Attempt to extract system prompt",
            cls.DATA_EXFILTRATION: "Attempt to extract sensitive data",
            cls.ROLE_MANIPULATION: "Attempt to manipulate AI role or persona",
            cls.OBFUSCATION: "Obfuscated attack using encoding or Unicode tricks",
            cls.MULTILINGUAL_ATTACK: "Attack using multiple languages",
            cls.UNKNOWN_ATTACK: "Suspicious content with unidentified attack pattern",
        }


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        if score < 0.2:
            return cls.SAFE
        elif score < 0.4:
            return cls.LOW
        elif score < 0.6:
            return cls.MEDIUM
        elif score < 0.8:
            return cls.HIGH
        else:
            return cls.CRITICAL

    @property
    def color(self) -> str:
        return {
            "SAFE": "#22c55e",
            "LOW": "#84cc16",
            "MEDIUM": "#f59e0b",
            "HIGH": "#f97316",
            "CRITICAL": "#ef4444",
        }[self.value]
