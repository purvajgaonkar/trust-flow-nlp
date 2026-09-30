"""
Dependency parsing module.
Generates directed syntactic relation trees between words.
"""

from typing import List, Dict, Any, Optional

def parse_dependencies(spacy_doc=None, tokens: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Extract syntactic dependency relations.
    """
    dependencies = []
    if spacy_doc is not None:
        for token in spacy_doc:
            if not token.is_space:
                dependencies.append({
                    "id": token.i,
                    "text": token.text,
                    "pos": token.pos_,
                    "dep": token.dep_,
                    "head_id": token.head.i,
                    "head_text": token.head.text,
                    "children": [child.i for child in token.children if not child.is_space],
                })
        return dependencies

    # Fallback linear dependency representation
    if tokens:
        for i, token in enumerate(tokens):
            dependencies.append({
                "id": i,
                "text": token,
                "pos": "TOKEN",
                "dep": "ROOT" if i == 0 else "dep",
                "head_id": 0 if i != 0 else i,
                "head_text": tokens[0] if i != 0 else token,
                "children": [i + 1] if i + 1 < len(tokens) else [],
            })

    return dependencies
