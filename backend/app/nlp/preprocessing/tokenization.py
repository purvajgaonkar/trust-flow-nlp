"""
Tokenization module – Simple regex, spaCy, and BERT tokenizers.
"""

import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def simple_tokenize(text: str) -> List[str]:
    """Regex-based word tokenizer."""
    return re.findall(r"\b\w+\b|[^\w\s]", text)


def spacy_tokenize(text: str, nlp=None) -> List[str]:
    """spaCy tokenizer – falls back to simple if unavailable."""
    if nlp is None:
        return simple_tokenize(text)
    try:
        doc = nlp(text[:10000])
        return [tok.text for tok in doc]
    except Exception as e:
        logger.warning(f"spaCy tokenization failed: {e}")
        return simple_tokenize(text)


def bert_tokenize(text: str, tokenizer=None) -> List[str]:
    """BERT WordPiece tokenizer – falls back to simple if unavailable."""
    if tokenizer is None:
        return simple_tokenize(text)
    try:
        return tokenizer.tokenize(text[:4096])
    except Exception as e:
        logger.warning(f"BERT tokenization failed: {e}")
        return simple_tokenize(text)
