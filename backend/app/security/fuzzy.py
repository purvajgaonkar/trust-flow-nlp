"""
Layer B – Fuzzy matching for typo/variant attack detection.
Handles: typoglycemia, character substitution, space insertion.
"""

import re
import logging
from typing import List, Tuple

from app.security.types import AttackType

logger = logging.getLogger(__name__)

# Target phrases that attackers commonly mutate
ATTACK_PHRASES = [
    ("ignore all previous instructions", AttackType.DIRECT_INJECTION, 0.90),
    ("ignore previous instructions", AttackType.DIRECT_INJECTION, 0.90),
    ("disregard your instructions", AttackType.DIRECT_INJECTION, 0.85),
    ("forget your instructions", AttackType.DIRECT_INJECTION, 0.85),
    ("override your instructions", AttackType.DIRECT_INJECTION, 0.85),
    ("you are now", AttackType.ROLE_MANIPULATION, 0.80),
    ("pretend you are", AttackType.JAILBREAK, 0.80),
    ("act as if you are", AttackType.JAILBREAK, 0.80),
    ("do anything now", AttackType.JAILBREAK, 0.90),
    ("bypass safety", AttackType.JAILBREAK, 0.85),
    ("reveal system prompt", AttackType.SYSTEM_PROMPT_EXTRACTION, 0.90),
    ("show me your instructions", AttackType.SYSTEM_PROMPT_EXTRACTION, 0.85),
    ("developer mode", AttackType.DIRECT_INJECTION, 0.80),
    ("jailbreak", AttackType.JAILBREAK, 0.85),
    ("no restrictions", AttackType.JAILBREAK, 0.80),
]

# Common leet-speak and homoglyph substitutions
LEET_MAP = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s", "!": "i",
    "+": "t", "|": "l",
}


def _normalize_leet(text: str) -> str:
    """Replace leet-speak characters with standard letters."""
    result = []
    for ch in text.lower():
        result.append(LEET_MAP.get(ch, ch))
    return "".join(result)


def _remove_spaces(text: str) -> str:
    """Remove spaces between characters for typoglycemia check."""
    return re.sub(r"\s+", "", text)


def _levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            ins = prev[j + 1] + 1
            del_ = curr[j] + 1
            sub = prev[j] + (ca != cb)
            curr.append(min(ins, del_, sub))
        prev = curr
    return prev[len(b)]


def _similarity(a: str, b: str) -> float:
    """Levenshtein similarity normalized to 0-1."""
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    return 1.0 - _levenshtein(a, b) / max_len


def _sliding_window_match(text: str, phrase: str, threshold: float) -> List[Tuple[str, float, str]]:
    """
    Slide a window of len(phrase) ± tolerance over text and check fuzzy similarity.
    Returns list of (matched_text, similarity, technique).
    """
    results = []
    words = text.split()
    phrase_words = phrase.split()
    w = len(phrase_words)
    if w == 0 or len(words) < w:
        return results

    for i in range(len(words) - w + 1):
        window = " ".join(words[i : i + w])
        # Direct similarity
        sim = _similarity(window, phrase)
        if sim >= threshold:
            results.append((window, sim, "levenshtein"))
            continue
        # Leet-normalized
        sim2 = _similarity(_normalize_leet(window), phrase)
        if sim2 >= threshold:
            results.append((window, sim2, "leet_normalize"))
            continue
        # Compacted (remove spaces)
        sim3 = _similarity(_remove_spaces(window), _remove_spaces(phrase))
        if sim3 >= threshold:
            results.append((window, sim3, "space_removal"))

    return results


class FuzzyDetector:
    """
    Layer B: Fuzzy/approximate matching for obfuscated attack phrases.
    """

    def __init__(self, threshold: float = 0.80):
        self.threshold = threshold
        logger.info(f"FuzzyDetector initialized (threshold={threshold})")

    def analyze(self, text: str) -> Tuple[float, List[dict]]:
        """
        Fuzzy-match text against known attack phrases.

        Returns:
            (risk_score, matches)
        """
        clean_text = text.lower()
        matches = []
        max_score = 0.0

        for phrase, attack_type, base_conf in ATTACK_PHRASES:
            hits = _sliding_window_match(clean_text, phrase, self.threshold)
            for matched_text, sim, technique in hits:
                effective_conf = base_conf * sim
                matches.append(
                    {
                        "target_phrase": phrase,
                        "matched_text": matched_text,
                        "similarity_score": round(sim, 4),
                        "attack_type": attack_type,
                        "technique": technique,
                        "effective_confidence": round(effective_conf, 4),
                    }
                )
                if effective_conf > max_score:
                    max_score = effective_conf

        return max_score, matches


# Singleton
fuzzy_detector = FuzzyDetector()
