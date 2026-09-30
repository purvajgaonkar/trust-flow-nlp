"""
Self-Consistency verification module.
Evaluates consensus across multiple sampled generations to measure claim stability.
"""

from typing import List, Dict, Any

def evaluate_self_consistency(claim: str, sampled_responses: List[str]) -> Dict[str, Any]:
    """
    Measures how consistently a claim appears across multiple sampled model responses.
    """
    if not sampled_responses:
        return {
            "consistency_score": 1.0,
            "sample_count": 0,
            "status": "NO_SAMPLES",
            "agreement_rate": 1.0,
        }

    claim_words = set(claim.lower().split()) - {"the", "a", "an", "is", "was", "in", "by", "of", "and"}
    agreements = 0

    for sample in sampled_responses:
        s_words = set(sample.lower().split())
        overlap = len(claim_words.intersection(s_words)) / max(1, len(claim_words))
        if overlap >= 0.5:
            agreements += 1

    agreement_rate = agreements / len(sampled_responses)
    return {
        "consistency_score": round(agreement_rate, 4),
        "sample_count": len(sampled_responses),
        "status": "HIGH_CONSISTENCY" if agreement_rate >= 0.7 else ("MODERATE_CONSISTENCY" if agreement_rate >= 0.4 else "LOW_CONSISTENCY"),
        "agreement_rate": round(agreement_rate, 4),
    }
