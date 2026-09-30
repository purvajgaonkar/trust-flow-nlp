"""
Claim Extraction module.
Decomposes complex response text into atomic, verifiable factual claims,
extracting associated entities and SPO (subject-predicate-object) triples.
"""

import re
import uuid
from typing import List, Dict, Any

def extract_atomic_claims(text: str) -> List[Dict[str, Any]]:
    """
    Deconstructs generated response into individual atomic claims.
    """
    if not text or not text.strip():
        return []

    # 1. Segment into raw sentences
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    claims = []

    for sentence in sentences:
        s = sentence.strip()
        if not s or len(s) < 5:
            continue

        # Check for compound sentences conjoined by coordinating conjunctions
        parts = re.split(r",?\s+(?:and|but|while|whereas)\s+", s)
        if len(parts) > 1 and all(len(p.strip()) > 15 for p in parts):
            for part in parts:
                p = part.strip()
                if not p.endswith("."):
                    p += "."
                claims.append(_build_claim_obj(p))
        else:
            claims.append(_build_claim_obj(s))

    return claims

def _build_claim_obj(claim_text: str) -> Dict[str, Any]:
    # Extract entities and SPO heuristic
    words = claim_text.replace(".", "").replace(",", "").split()
    entities = [w for w in words if w and w[0].isupper() and len(w) > 1]
    
    # Subject-Predicate-Object heuristic
    spo = {"subject": entities[0] if entities else (words[0] if words else ""), "predicate": "related_to", "object": entities[-1] if len(entities) > 1 else (words[-1] if words else "")}
    
    return {
        "id": f"claim_{uuid.uuid4().hex[:6]}",
        "text": claim_text,
        "entities": entities,
        "spo": spo,
        "is_verifiable": len(entities) > 0 or any(c.isdigit() for c in claim_text),
    }
