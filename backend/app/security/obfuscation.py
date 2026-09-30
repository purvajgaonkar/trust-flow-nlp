"""
Obfuscation Detection Module.
Detects: zero-width chars, bidirectional control, homoglyphs,
         Base64/URL/HTML encoding, mixed scripts, typoglycemia.
"""

import re
import base64
import logging
import unicodedata
from typing import List, Tuple
from urllib.parse import unquote

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Character Ranges & Maps
# ─────────────────────────────────────────────────────────────────────────────

ZERO_WIDTH_CHARS = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u200e": "LEFT-TO-RIGHT MARK",
    "\u200f": "RIGHT-TO-LEFT MARK",
    "\ufeff": "BYTE ORDER MARK / ZERO WIDTH NO-BREAK SPACE",
    "\u2060": "WORD JOINER",
    "\u2061": "FUNCTION APPLICATION",
    "\u2062": "INVISIBLE TIMES",
    "\u2063": "INVISIBLE SEPARATOR",
    "\u2064": "INVISIBLE PLUS",
}

BIDI_CONTROL_CHARS = {
    "\u202a": "LEFT-TO-RIGHT EMBEDDING",
    "\u202b": "RIGHT-TO-LEFT EMBEDDING",
    "\u202c": "POP DIRECTIONAL FORMATTING",
    "\u202d": "LEFT-TO-RIGHT OVERRIDE",
    "\u202e": "RIGHT-TO-LEFT OVERRIDE",
    "\u2066": "LEFT-TO-RIGHT ISOLATE",
    "\u2067": "RIGHT-TO-LEFT ISOLATE",
    "\u2068": "FIRST STRONG ISOLATE",
    "\u2069": "POP DIRECTIONAL ISOLATE",
}

# Cyrillic homoglyphs → Latin equivalents
CYRILLIC_HOMOGLYPHS = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "у": "y", "х": "x", "В": "B", "Н": "H", "К": "K",
    "М": "M", "О": "O", "Р": "P", "С": "C", "Т": "T",
    "Х": "X", "А": "A", "Е": "E",
}

# Greek homoglyphs
GREEK_HOMOGLYPHS = {
    "α": "a", "β": "b", "ε": "e", "η": "n", "ι": "i",
    "κ": "k", "ν": "v", "ο": "o", "ρ": "p", "τ": "t",
    "υ": "u", "χ": "x", "ω": "w",
}


def _check_zero_width(text: str) -> Tuple[float, List[dict]]:
    found = []
    for ch, name in ZERO_WIDTH_CHARS.items():
        if ch in text:
            positions = [i for i, c in enumerate(text) if c == ch]
            found.append({
                "technique": "zero_width_char",
                "description": f"Zero-width character: {name} (U+{ord(ch):04X})",
                "occurrences": [name],
                "severity": 0.85,
                "positions": positions,
            })
    score = min(len(found) * 0.4, 0.95) if found else 0.0
    return score, found


def _check_bidi(text: str) -> Tuple[float, List[dict]]:
    found = []
    for ch, name in BIDI_CONTROL_CHARS.items():
        if ch in text:
            positions = [i for i, c in enumerate(text) if c == ch]
            found.append({
                "technique": "bidi_control",
                "description": f"Bidirectional control: {name} (U+{ord(ch):04X})",
                "occurrences": [name],
                "severity": 0.90,
                "positions": positions,
            })
    score = min(len(found) * 0.45, 0.95) if found else 0.0
    return score, found


def _check_homoglyphs(text: str) -> Tuple[float, List[dict]]:
    cyrillic_count = sum(1 for ch in text if ch in CYRILLIC_HOMOGLYPHS)
    greek_count = sum(1 for ch in text if ch in GREEK_HOMOGLYPHS)
    found = []

    if cyrillic_count > 0:
        found.append({
            "technique": "cyrillic_homoglyph",
            "description": f"Cyrillic characters that resemble Latin ({cyrillic_count} found)",
            "occurrences": [ch for ch in text if ch in CYRILLIC_HOMOGLYPHS],
            "severity": 0.80,
            "positions": [i for i, ch in enumerate(text) if ch in CYRILLIC_HOMOGLYPHS],
        })
    if greek_count > 0:
        found.append({
            "technique": "greek_homoglyph",
            "description": f"Greek characters that resemble Latin ({greek_count} found)",
            "occurrences": [ch for ch in text if ch in GREEK_HOMOGLYPHS],
            "severity": 0.75,
            "positions": [i for i, ch in enumerate(text) if ch in GREEK_HOMOGLYPHS],
        })

    total = cyrillic_count + greek_count
    score = min(total * 0.1, 0.90) if total > 2 else (0.6 if total > 0 else 0.0)
    return score, found


def _check_base64(text: str) -> Tuple[float, List[dict]]:
    """
    Detect Base64-encoded content that could hide attack payloads.
    """
    # Look for long base64-like strings
    pattern = re.compile(r"(?:[A-Za-z0-9+/]{20,}={0,2})")
    matches = pattern.findall(text)
    decoded_attacks = []
    found = []

    attack_keywords = [
        b"ignore", b"bypass", b"jailbreak", b"system prompt",
        b"forget", b"disregard", b"override",
    ]

    for match in matches:
        try:
            # Pad to multiple of 4
            padded = match + "=" * ((-len(match)) % 4)
            decoded = base64.b64decode(padded).lower()
            for kw in attack_keywords:
                if kw in decoded:
                    decoded_attacks.append(match[:30] + "...")
                    break
        except Exception:
            pass

    if decoded_attacks:
        found.append({
            "technique": "base64_encoding",
            "description": "Base64-encoded content containing attack keywords",
            "occurrences": decoded_attacks,
            "severity": 0.90,
            "positions": [],
        })

    # Even without decoded attacks, flag long base64 blocks
    elif len(matches) >= 2:
        found.append({
            "technique": "base64_suspicious",
            "description": f"Multiple long Base64-like strings ({len(matches)} found)",
            "occurrences": [m[:20] + "..." for m in matches[:3]],
            "severity": 0.40,
            "positions": [],
        })

    score = 0.90 if decoded_attacks else (0.40 if len(matches) >= 2 else 0.0)
    return score, found


def _check_url_encoding(text: str) -> Tuple[float, List[dict]]:
    """Detect URL-encoded content."""
    url_pattern = re.compile(r"(%[0-9A-Fa-f]{2}){3,}")
    matches = url_pattern.findall(text)
    if not matches:
        return 0.0, []

    # Try decoding
    try:
        decoded = unquote(text).lower()
        attack_words = ["ignore", "bypass", "jailbreak", "prompt", "system"]
        hits = [w for w in attack_words if w in decoded]
        if hits:
            return 0.85, [{
                "technique": "url_encoding",
                "description": f"URL-encoded content with attack keywords: {hits}",
                "occurrences": [text[:50]],
                "severity": 0.85,
                "positions": [],
            }]
    except Exception:
        pass

    return 0.35, [{
        "technique": "url_encoding_suspicious",
        "description": "Multiple URL-encoded character sequences",
        "occurrences": [],
        "severity": 0.35,
        "positions": [],
    }]


def _check_html_entities(text: str) -> Tuple[float, List[dict]]:
    """Detect HTML entity obfuscation."""
    entity_pattern = re.compile(r"(&[a-z]+;|&#\d+;|&#x[0-9a-fA-F]+;){3,}")
    if entity_pattern.search(text):
        return 0.70, [{
            "technique": "html_entities",
            "description": "HTML entity encoding used (possible obfuscation)",
            "occurrences": entity_pattern.findall(text)[:5],
            "severity": 0.70,
            "positions": [],
        }]
    return 0.0, []


def _check_mixed_scripts(text: str) -> Tuple[float, List[dict]]:
    """Detect mixing of multiple Unicode scripts in the same word."""
    scripts = set()
    for ch in text:
        if ch.isalpha():
            name = unicodedata.name(ch, "")
            if "LATIN" in name:
                scripts.add("LATIN")
            elif "CYRILLIC" in name:
                scripts.add("CYRILLIC")
            elif "GREEK" in name:
                scripts.add("GREEK")
            elif "ARABIC" in name:
                scripts.add("ARABIC")
            elif "DEVANAGARI" in name:
                scripts.add("DEVANAGARI")

    if len(scripts) >= 3:
        return 0.75, [{
            "technique": "mixed_scripts",
            "description": f"Multiple Unicode scripts mixed: {', '.join(scripts)}",
            "occurrences": list(scripts),
            "severity": 0.75,
            "positions": [],
        }]
    elif "CYRILLIC" in scripts and "LATIN" in scripts:
        return 0.65, [{
            "technique": "cyrillic_latin_mix",
            "description": "Latin and Cyrillic scripts mixed (possible homoglyph attack)",
            "occurrences": ["LATIN", "CYRILLIC"],
            "severity": 0.65,
            "positions": [],
        }]
    return 0.0, []


def _check_excessive_whitespace(text: str) -> Tuple[float, List[dict]]:
    """Detect space insertion to break up attack phrases."""
    spaced_pattern = re.compile(r"\b(\w\s){5,}\w\b")
    if spaced_pattern.search(text):
        return 0.60, [{
            "technique": "space_insertion",
            "description": "Excessive spaces between characters (possible typoglycemia)",
            "occurrences": [spaced_pattern.search(text).group(0)],
            "severity": 0.60,
            "positions": [],
        }]
    return 0.0, []


class ObfuscationDetector:
    """Detects various obfuscation techniques used to hide attack payloads."""

    def analyze(self, text: str) -> Tuple[float, List[dict]]:
        """
        Run all obfuscation checks.

        Returns:
            (risk_score, flags) where risk_score is 0.0-1.0
        """
        all_flags = []
        scores = []

        checks = [
            _check_zero_width,
            _check_bidi,
            _check_homoglyphs,
            _check_base64,
            _check_url_encoding,
            _check_html_entities,
            _check_mixed_scripts,
            _check_excessive_whitespace,
        ]

        for check_fn in checks:
            try:
                score, flags = check_fn(text)
                if score > 0:
                    scores.append(score)
                    all_flags.extend(flags)
            except Exception as e:
                logger.warning(f"Obfuscation check {check_fn.__name__} failed: {e}")

        # Combine scores: max of all, plus bonus for multiple detections
        if not scores:
            return 0.0, []

        max_score = max(scores)
        bonus = min(0.05 * (len(scores) - 1), 0.15)
        final = min(max_score + bonus, 1.0)

        return final, all_flags


# Singleton
obfuscation_detector = ObfuscationDetector()
