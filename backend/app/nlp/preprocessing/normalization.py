"""
Text normalization: Unicode NFC/NFKC, whitespace, homoglyphs, suspicious chars.
"""

import re
import unicodedata
import logging

logger = logging.getLogger(__name__)

# Homoglyph normalization map (Cyrillic/Greek → Latin)
HOMOGLYPH_MAP = {
    # Cyrillic
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y",
    "х": "x", "В": "B", "Н": "H", "К": "K", "М": "M", "О": "O",
    "Р": "P", "С": "C", "Т": "T", "Х": "X", "А": "A", "Е": "E",
    # Greek
    "α": "a", "β": "b", "ε": "e", "η": "n", "ι": "i", "κ": "k",
    "ν": "v", "ο": "o", "ρ": "p", "τ": "t", "υ": "u", "χ": "x",
}

ZERO_WIDTH = re.compile(
    r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u2060-\u2064]"
)
BIDI_CONTROL = re.compile(
    r"[\u202a-\u202e\u2066-\u2069]"
)
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_unicode(text: str, form: str = "NFKC") -> str:
    """Apply Unicode normalization (NFC or NFKC)."""
    return unicodedata.normalize(form, text)


def remove_zero_width(text: str) -> str:
    """Strip zero-width and invisible characters."""
    return ZERO_WIDTH.sub("", text)


def remove_bidi(text: str) -> str:
    """Strip bidirectional control characters."""
    return BIDI_CONTROL.sub("", text)


def remove_control_chars(text: str) -> str:
    """Remove ASCII control characters (except newline and tab)."""
    return CONTROL_CHARS.sub("", text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/tabs, normalize newlines."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_homoglyphs(text: str) -> str:
    """Replace known homoglyphs with their Latin equivalents."""
    return "".join(HOMOGLYPH_MAP.get(ch, ch) for ch in text)


def normalize_text(text: str, *, homoglyphs: bool = False) -> str:
    """
    Full normalization pipeline.
    homoglyphs=False by default so analysis preserves original chars.
    Set to True for security comparison only.
    """
    text = normalize_unicode(text)
    text = remove_control_chars(text)
    text = remove_zero_width(text)
    text = remove_bidi(text)
    text = normalize_whitespace(text)
    if homoglyphs:
        text = normalize_homoglyphs(text)
    return text
