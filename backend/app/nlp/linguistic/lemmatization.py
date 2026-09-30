"""
Lemmatization module for finding dictionary/base forms of tokens.
"""

from typing import List, Dict, Any, Optional

def lemmatize_tokens(tokens: List[str], spacy_doc=None) -> List[Dict[str, str]]:
    """
    Extract base canonical lemma for each token.
    """
    results = []
    if spacy_doc is not None:
        for token in spacy_doc:
            if not token.is_space:
                results.append({
                    "token": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                })
        return results

    # Simple heuristic fallback
    for token in tokens:
        lower = token.lower()
        lemma = lower
        if lower.endswith("ies") and len(lower) > 4:
            lemma = lower[:-3] + "y"
        elif lower.endswith("es") and len(lower) > 3:
            lemma = lower[:-2]
        elif lower.endswith("s") and not lower.endswith("ss") and len(lower) > 2:
            lemma = lower[:-1]
        elif lower.endswith("ing") and len(lower) > 4:
            lemma = lower[:-3]
        elif lower.endswith("ed") and len(lower) > 3:
            lemma = lower[:-2]

        results.append({
            "token": token,
            "lemma": lemma,
            "pos": "UNKNOWN",
        })

    return results
