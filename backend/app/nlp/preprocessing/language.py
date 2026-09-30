"""
Language detection module.
Supports: English, Hindi, Marathi, Hinglish (code-mixed).
Uses langdetect with Unicode-based script heuristics.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Unicode ranges for Devanagari script (Hindi & Marathi)
DEVANAGARI_RANGE = re.compile(r"[\u0900-\u097F]")

# Marathi-specific common words (not found in standard Hindi)
MARATHI_MARKERS = [
    "आहे", "नाही", "होते", "मला", "तुम्ही", "आम्ही", "येथे",
    "करणे", "सांगा", "कसे", "केले", "जाते", "येईल",
]

# Hindi-specific common words
HINDI_MARKERS = [
    "है", "हैं", "नहीं", "मैं", "आप", "हम", "यहाँ",
    "करना", "बताओ", "कैसे", "किया", "जाना", "आएगा",
]

# Hinglish indicators – Devanagari mixed with Latin
HINGLISH_LATIN_RATIO_MIN = 0.10  # At least 10% of words are Latin in a Devanagari text


def _devanagari_ratio(text: str) -> float:
    """Fraction of alphabetic characters that are Devanagari."""
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return 0.0
    dev = [c for c in alpha if "\u0900" <= c <= "\u097F"]
    return len(dev) / len(alpha)


def _latin_word_ratio(text: str) -> float:
    """Fraction of whitespace-separated tokens that are purely Latin."""
    tokens = text.split()
    if not tokens:
        return 0.0
    latin = [t for t in tokens if re.fullmatch(r"[A-Za-z0-9\-']+", t)]
    return len(latin) / len(tokens)


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect the language of text.

    Returns:
        (language, confidence)  where language ∈ {english, hindi, marathi, hinglish, unknown}
    """
    dev_ratio = _devanagari_ratio(text)
    latin_ratio = _latin_word_ratio(text)

    # ── Devanagari script ────────────────────────────────────────────────────
    if dev_ratio > 0.5:
        # Check for Hinglish (code-mixed Devanagari + Latin)
        if latin_ratio >= HINGLISH_LATIN_RATIO_MIN:
            conf = 0.70 + min(dev_ratio * 0.2, 0.20)
            return "hinglish", round(conf, 3)

        # Distinguish Hindi vs Marathi by marker words
        marathi_hits = sum(1 for w in MARATHI_MARKERS if w in text)
        hindi_hits = sum(1 for w in HINDI_MARKERS if w in text)

        if marathi_hits > hindi_hits:
            conf = 0.65 + min(marathi_hits * 0.05, 0.25)
            return "marathi", round(conf, 3)
        else:
            conf = 0.65 + min(hindi_hits * 0.05, 0.25)
            return "hindi", round(conf, 3)

    # ── Partial Devanagari (Hinglish) ────────────────────────────────────────
    if 0.05 < dev_ratio <= 0.5:
        return "hinglish", round(0.60 + dev_ratio * 0.3, 3)

    # ── Pure Latin / English ─────────────────────────────────────────────────
    if latin_ratio > 0.7:
        # Try langdetect for finer-grained detection
        try:
            from langdetect import detect, DetectorFactory
            DetectorFactory.seed = 42
            lang = detect(text)
            if lang == "en":
                return "english", 0.90
            elif lang in ("hi",):
                return "hindi", 0.75
            elif lang in ("mr",):
                return "marathi", 0.75
            else:
                return "english", 0.60  # Default for Latin-script text
        except Exception:
            pass
        return "english", 0.80

    return "unknown", 0.40
