"""
Hallucination Scoring module.
Synthesizes signals from NLI verification, evidence coverage, semantic similarity,
and entity consistency into an explainable hallucination risk score.
"""

from typing import List, Dict, Any

def compute_hallucination_score(
    claims_analysis: List[Dict[str, Any]],
    avg_similarity: float = 0.0,
    has_contradiction: bool = False
) -> Dict[str, Any]:
    """
    Computes overall hallucination risk from 0.0 (Grounded) to 1.0 (Completely Hallucinated).
    """
    total_claims = len(claims_analysis)
    if total_claims == 0:
        return {
            "score": 0.0,
            "risk_level": "LOW",
            "groundedness": 1.0,
            "explanation": "No factual claims requiring verification found.",
            "metrics": {
                "supported_pct": 1.0,
                "contradicted_pct": 0.0,
                "unverified_pct": 0.0,
            }
        }

    supported = sum(1 for c in claims_analysis if c.get("verification_status") == "SUPPORTED")
    contradicted = sum(1 for c in claims_analysis if c.get("verification_status") == "CONTRADICTED")
    unverified = sum(1 for c in claims_analysis if c.get("verification_status") in ("UNVERIFIED", "NEUTRAL"))

    supp_pct = supported / total_claims
    contra_pct = contradicted / total_claims
    unver_pct = unverified / total_claims

    # Groundedness is primarily supported claims
    groundedness = round(supp_pct + (unver_pct * 0.2), 3)
    groundedness = min(1.0, max(0.0, groundedness))

    # Risk score calculation
    # Contradictions are heavily penalized
    risk = (contra_pct * 0.7) + (unver_pct * 0.3)
    if has_contradiction or contradicted > 0:
        risk = max(risk, 0.65)

    risk = min(1.0, max(0.0, round(risk, 3)))

    if risk >= 0.7:
        risk_level = "HIGH"
    elif risk >= 0.35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "score": risk,
        "risk_level": risk_level,
        "groundedness": groundedness,
        "explanation": f"{supported}/{total_claims} claims verified by evidence. {contradicted} contradicted, {unverified} unverified.",
        "metrics": {
            "supported_pct": round(supp_pct, 3),
            "contradicted_pct": round(contra_pct, 3),
            "unverified_pct": round(unver_pct, 3),
        }
    }
