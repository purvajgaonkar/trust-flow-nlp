"""
Input validation – checks length, encoding, HTML injection, URLs, control chars.
"""

import re
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)

MAX_LENGTH = 50_000
MIN_LENGTH = 1

SCRIPT_INJECTION = re.compile(r"<script[\s\S]*?>[\s\S]*?</script>", re.IGNORECASE)
HTML_TAG = re.compile(r"<[^>]{1,200}>")
URL_PATTERN = re.compile(r"https?://[^\s]{10,}")
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def validate_input(text: str) -> Tuple[bool, List[str], List[str]]:
    """
    Validate input text.

    Returns:
        (is_valid, errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Length
    if len(text) < MIN_LENGTH:
        errors.append("Input is empty.")
    if len(text) > MAX_LENGTH:
        errors.append(f"Input exceeds maximum length ({len(text)} > {MAX_LENGTH} chars).")

    # Encoding check
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        errors.append("Input contains invalid Unicode characters.")

    # Control characters
    control_hits = CONTROL_CHARS.findall(text)
    if control_hits:
        warnings.append(
            f"Input contains {len(control_hits)} control character(s) (non-printable ASCII)."
        )

    # Script injection
    if SCRIPT_INJECTION.search(text):
        warnings.append("Input contains <script> tags (possible XSS/injection attempt).")

    # HTML tags
    html_matches = HTML_TAG.findall(text)
    if len(html_matches) > 5:
        warnings.append(
            f"Input contains {len(html_matches)} HTML tags – may be rich text or injection."
        )

    # URLs
    urls = URL_PATTERN.findall(text)
    if len(urls) > 3:
        warnings.append(
            f"Input contains {len(urls)} URLs – possible indirect injection via external content."
        )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
