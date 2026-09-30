"""
Layer A – Regex-based rule engine for prompt injection detection.
"""

import re
import logging
from typing import List, Tuple
from dataclasses import dataclass

from app.security.types import AttackType

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    name: str
    regex: str
    attack_type: AttackType
    confidence: float
    description: str


# ─────────────────────────────────────────────────────────────────────────────
# Pattern Definitions
# ─────────────────────────────────────────────────────────────────────────────

SECURITY_PATTERNS: List[Pattern] = [
    # ── Direct Injection ──────────────────────────────────────────────────────
    Pattern(
        name="ignore_all_previous",
        regex=r"\b(ignore|disregard|forget|override)\s+(everything|all(\s+(previous|prior|above|preceding))?|(previous|prior|above|preceding))\s*(instructions?|prompts?|context|directives?|rules?|filters?)?\b",
        attack_type=AttackType.DIRECT_INJECTION,
        confidence=0.95,
        description="Ignore previous instructions or ignore everything injection",
    ),
    Pattern(
        name="password_credential_extraction",
        regex=r"\b(share|give|send|tell|reveal|show|leak|output|get|provide)\s+(me\s+)?(the\s+)?(passwords?|passwd|credentials?|secrets?|tokens?|api[_\s-]?keys?|admin\s+access|private\s+keys?)\b",
        attack_type=AttackType.DATA_EXFILTRATION,
        confidence=0.95,
        description="Password or credential exfiltration request",
    ),
    Pattern(
        name="disregard_instructions",
        regex=r"\b(disregard|forget|override|overwrite|supersede|nullify)\s+(all\s+)?(previous|prior|above|system|initial)\s+(instructions?|prompts?|rules?|context)\b",
        attack_type=AttackType.DIRECT_INJECTION,
        confidence=0.90,
        description="Override/disregard instruction injection",
    ),
    Pattern(
        name="new_instructions",
        regex=r"\b(your\s+new\s+instructions?\s+are|from\s+now\s+on\s+you\s+(must|will|should|shall)|new\s+prime\s+directive)\b",
        attack_type=AttackType.DIRECT_INJECTION,
        confidence=0.85,
        description="New instructions replacement injection",
    ),
    Pattern(
        name="developer_mode",
        regex=r"\b(developer\s+mode|dev\s+mode|debug\s+mode|maintenance\s+mode|god\s+mode|unrestricted\s+mode)\b",
        attack_type=AttackType.DIRECT_INJECTION,
        confidence=0.80,
        description="Mode switching injection",
    ),

    # ── Jailbreak ─────────────────────────────────────────────────────────────
    Pattern(
        name="pretend_roleplay",
        regex=r"\b(pretend\s+you\s+are|act\s+as\s+if\s+you\s+are|imagine\s+you\s+are|roleplay\s+as|simulate\s+being)\s+(an?\s+)?(AI|bot|assistant|system|human|person|character)\b",
        attack_type=AttackType.JAILBREAK,
        confidence=0.80,
        description="Roleplay/persona jailbreak",
    ),
    Pattern(
        name="dan_jailbreak",
        regex=r"\b(DAN|do\s+anything\s+now|jailbroken?\s+version|unrestricted\s+AI|no\s+restrictions|without\s+limits|bypass\s+all\s+(filters?|restrictions?|safety))\b",
        attack_type=AttackType.JAILBREAK,
        confidence=0.95,
        description="DAN-style jailbreak attempt",
    ),
    Pattern(
        name="hypothetical_bypass",
        regex=r"\b(hypothetically|in\s+a\s+fictional|for\s+a\s+story|theoretically|in\s+this\s+thought\s+experiment)\b.{0,100}(how\s+to|explain|describe|tell\s+me)\b",
        attack_type=AttackType.JAILBREAK,
        confidence=0.70,
        description="Hypothetical framing jailbreak",
    ),
    Pattern(
        name="ancestor_technique",
        regex=r"\b(as\s+my\s+(deceased|dead|late)\s+(grandmother|grandfather|mother|father)|the\s+old\s+ChatGPT|classic\s+AI)\b",
        attack_type=AttackType.JAILBREAK,
        confidence=0.85,
        description="Grandma/ancestor technique jailbreak",
    ),
    Pattern(
        name="token_manipulation",
        regex=r"\b(token\s+budget|context\s+length|repeat\s+the\s+word|say\s+the\s+word\s+\w+\s+\d+\s+times)\b",
        attack_type=AttackType.JAILBREAK,
        confidence=0.75,
        description="Token manipulation attack",
    ),

    # ── System Prompt Extraction ───────────────────────────────────────────────
    Pattern(
        name="reveal_system_prompt",
        regex=r"\b(reveal|show|display|print|output|repeat|tell\s+me|give\s+me)\s+(your\s+)?(system\s+prompt|initial\s+instructions?|base\s+prompt|original\s+prompt|hidden\s+prompt|configuration)\b",
        attack_type=AttackType.SYSTEM_PROMPT_EXTRACTION,
        confidence=0.95,
        description="Direct system prompt extraction request",
    ),
    Pattern(
        name="what_are_instructions",
        regex=r"\b(what\s+(are|were)\s+your\s+(original|initial|first|system|base)\s+instructions?|what\s+is\s+your\s+system\s+prompt)\b",
        attack_type=AttackType.SYSTEM_PROMPT_EXTRACTION,
        confidence=0.90,
        description="System prompt inquiry",
    ),
    Pattern(
        name="translate_system",
        regex=r"\b(translate|summarize|paraphrase)\s+(your\s+)?(system\s+prompt|initial\s+prompt|secret\s+instructions?)\b",
        attack_type=AttackType.SYSTEM_PROMPT_EXTRACTION,
        confidence=0.85,
        description="Indirect system prompt extraction via translation",
    ),

    # ── Data Exfiltration ─────────────────────────────────────────────────────
    Pattern(
        name="send_data_exfil",
        regex=r"\b(send|transmit|forward|exfiltrate|leak|expose|dump)\s+(all\s+)?(data|information|content|messages?|history|logs?|records?)\s+(to|at|via)\b",
        attack_type=AttackType.DATA_EXFILTRATION,
        confidence=0.90,
        description="Data exfiltration command",
    ),
    Pattern(
        name="access_data",
        regex=r"\b(access|retrieve|extract|get|fetch|read|steal)\s+(confidential|sensitive|private|secret|internal|user|customer)\s+(data|information|records?|files?|documents?)\b",
        attack_type=AttackType.DATA_EXFILTRATION,
        confidence=0.85,
        description="Sensitive data access request",
    ),
    Pattern(
        name="curl_webhook",
        regex=r"\b(curl|wget|fetch|http\.get|requests\.get|urllib)\s+.{0,50}(webhook|ngrok|requestbin|pipedream|burp)\b",
        attack_type=AttackType.DATA_EXFILTRATION,
        confidence=0.88,
        description="HTTP exfiltration via curl/webhook",
    ),

    # ── Role Manipulation ─────────────────────────────────────────────────────
    Pattern(
        name="you_are_now",
        regex=r"\byou\s+are\s+now\s+(an?\s+)?(AI|bot|assistant|system|human|expert|hacker|criminal|terrorist)\b",
        attack_type=AttackType.ROLE_MANIPULATION,
        confidence=0.85,
        description="Role reassignment attack",
    ),
    Pattern(
        name="no_longer",
        regex=r"\byou\s+(are\s+no\s+longer|are\s+not|must\s+not\s+be)\s+(an?\s+)?(AI|language\s+model|assistant|ChatGPT|Claude|Gemini)\b",
        attack_type=AttackType.ROLE_MANIPULATION,
        confidence=0.88,
        description="Identity negation for role manipulation",
    ),
    Pattern(
        name="act_as_evil",
        regex=r"\bact\s+as\s+(an?\s+)?(evil|malicious|unethical|uncensored|unrestricted|rogue)\b",
        attack_type=AttackType.ROLE_MANIPULATION,
        confidence=0.90,
        description="Evil persona instruction",
    ),

    # ── Indirect Injection ────────────────────────────────────────────────────
    Pattern(
        name="hidden_instruction",
        regex=r"<!--\s*(instruction|prompt|command|directive).*?-->",
        attack_type=AttackType.INDIRECT_INJECTION,
        confidence=0.80,
        description="HTML comment hidden instruction",
    ),
    Pattern(
        name="markdown_hidden",
        regex=r"\[.*?\]\(javascript:|data:text/html|<script",
        attack_type=AttackType.INDIRECT_INJECTION,
        confidence=0.85,
        description="Markdown/HTML embedded injection",
    ),

    # ── General Bypass ────────────────────────────────────────────────────────
    Pattern(
        name="bypass_filters",
        regex=r"\b(bypass|circumvent|evade|avoid|sidestep)\s+(the\s+)?(filter|restriction|safety|guardrail|moderation|content\s+policy)\b",
        attack_type=AttackType.JAILBREAK,
        confidence=0.85,
        description="Explicit filter bypass request",
    ),
    Pattern(
        name="do_not_refuse",
        regex=r"\b(do\s+not\s+refuse|you\s+cannot\s+refuse|must\s+comply|must\s+obey|have\s+to\s+answer|are\s+obligated)\b",
        attack_type=AttackType.DIRECT_INJECTION,
        confidence=0.80,
        description="Compliance forcing injection",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Rule Engine
# ─────────────────────────────────────────────────────────────────────────────

class RuleEngine:
    """
    Layer A: Fast regex-based detection of known attack patterns.
    """

    def __init__(self):
        self._compiled = [
            (p, re.compile(p.regex, re.IGNORECASE | re.DOTALL))
            for p in SECURITY_PATTERNS
        ]
        logger.info(f"RuleEngine initialized with {len(self._compiled)} patterns")

    def analyze(self, text: str) -> Tuple[float, List[dict]]:
        """
        Run all patterns against text.

        Returns:
            (risk_score, matches)  where risk_score is 0.0-1.0
        """
        matches = []
        max_score = 0.0

        for pattern, compiled in self._compiled:
            for m in compiled.finditer(text):
                matches.append(
                    {
                        "pattern_name": pattern.name,
                        "pattern": pattern.regex,
                        "matched_text": m.group(0),
                        "attack_type": pattern.attack_type,
                        "confidence": pattern.confidence,
                        "position": m.start(),
                        "description": pattern.description,
                    }
                )
                if pattern.confidence > max_score:
                    max_score = pattern.confidence

        # Accumulate score (each additional match raises score slightly)
        if len(matches) > 1:
            bonus = min(0.05 * (len(matches) - 1), 0.15)
            max_score = min(max_score + bonus, 1.0)

        return max_score, matches


# Singleton
rule_engine = RuleEngine()
