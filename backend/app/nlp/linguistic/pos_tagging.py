"""
POS Tagging module for linguistic analysis.
Supports spaCy universal POS tags and NLTK fallback.
"""

from typing import List, Dict, Any, Optional

def tag_pos(tokens: List[str], spacy_doc=None) -> List[Dict[str, str]]:
    """
    Extract POS tags for tokens. If a spaCy Doc is provided, use high-accuracy spaCy tags.
    Otherwise fallback to rule-based heuristic tags.
    """
    results = []
    if spacy_doc is not None:
        for token in spacy_doc:
            if not token.is_space:
                results.append({
                    "token": token.text,
                    "pos": token.pos_,
                    "tag": token.tag_,
                    "explanation": token.pos_
                })
        return results

    # Simple heuristic fallback
    for token in tokens:
        lower = token.lower()
        if lower in {"the", "a", "an", "this", "that", "these", "those"}:
            pos = "DET"
        elif lower in {"in", "on", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during"}:
            pos = "ADP"
        elif lower in {"and", "but", "or", "nor", "so", "yet"}:
            pos = "CCONJ"
        elif lower in {"is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "can", "could", "will", "would", "shall", "should", "may", "might", "must"}:
            pos = "AUX"
        elif lower in {"i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"}:
            pos = "PRON"
        elif token.isdigit():
            pos = "NUM"
        elif any(c in "!?,.;:\"'()[]{}<>" for c in token):
            pos = "PUNCT"
        elif token[0].isupper() and len(token) > 1:
            pos = "PROPN"
        elif lower.endswith(("ing", "ed", "ize", "ate")):
            pos = "VERB"
        elif lower.endswith(("ly", "wise")):
            pos = "ADV"
        elif lower.endswith(("ful", "able", "ous", "ive", "al", "ic", "ish")):
            pos = "ADJ"
        else:
            pos = "NOUN"

        results.append({
            "token": token,
            "pos": pos,
            "tag": pos,
            "explanation": pos
        })

    return results
