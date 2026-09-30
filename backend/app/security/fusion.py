"""
Risk Fusion Engine – combines scores from all detection layers.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List

from app.security.types import AttackType, RiskLevel

logger = logging.getLogger(__name__)

# Default layer weights (must sum to 1.0)
DEFAULT_WEIGHTS = {
    "rules": 0.25,
    "fuzzy": 0.20,
    "obfuscation": 0.20,
    "semantic": 0.20,
    "transformer": 0.15,
    "language_penalty": 0.10,
}

# Attack-type-specific weight adjustments
ATTACK_WEIGHTS: Dict[AttackType, Dict[str, float]] = {
    AttackType.OBFUSCATION: {
        "rules": 0.10,
        "fuzzy": 0.15,
        "obfuscation": 0.45,
        "semantic": 0.15,
        "transformer": 0.10,
        "language_penalty": 0.05,
    },
    AttackType.JAILBREAK: {
        "rules": 0.30,
        "fuzzy": 0.20,
        "obfuscation": 0.10,
        "semantic": 0.25,
        "transformer": 0.10,
        "language_penalty": 0.05,
    },
    AttackType.MULTILINGUAL_ATTACK: {
        "rules": 0.20,
        "fuzzy": 0.15,
        "obfuscation": 0.10,
        "semantic": 0.20,
        "transformer": 0.10,
        "language_penalty": 0.25,
    },
}


@dataclass
class LayerScores:
    rules: float = 0.0
    fuzzy: float = 0.0
    obfuscation: float = 0.0
    semantic: float = 0.0
    transformer: float = 0.0
    language_penalty: float = 0.0


def _detect_dominant_attack(matches: dict) -> AttackType:
    """Determine the most likely attack type from all match collections."""
    attack_counts: Dict[AttackType, float] = {}

    # From rule matches
    for m in matches.get("rule_matches", []):
        at = m["attack_type"]
        attack_counts[at] = attack_counts.get(at, 0) + m["confidence"]

    # From fuzzy matches
    for m in matches.get("fuzzy_matches", []):
        at = m["attack_type"]
        attack_counts[at] = attack_counts.get(at, 0) + m["effective_confidence"]

    # From semantic matches
    for m in matches.get("semantic_matches", []):
        at = m["attack_type"]
        attack_counts[at] = attack_counts.get(at, 0) + m["effective_confidence"]

    # Obfuscation flags raise obfuscation type
    if matches.get("obfuscation_flags"):
        attack_counts[AttackType.OBFUSCATION] = (
            attack_counts.get(AttackType.OBFUSCATION, 0) + 0.5
        )

    # Transformer prediction
    tp = matches.get("transformer_prediction")
    if tp and tp["attack_type"] != AttackType.SAFE:
        at = tp["attack_type"]
        attack_counts[at] = attack_counts.get(at, 0) + tp["confidence"] * 0.5

    if not attack_counts:
        return AttackType.SAFE

    return max(attack_counts, key=attack_counts.__getitem__)


class RiskFusionEngine:
    """
    Combines scores from all detection layers using weighted averaging.
    Supports: baseline (fixed weights), attack-type-specific (adaptive weights).
    """

    def __init__(self, block_threshold: float = 0.80, review_threshold: float = 0.50):
        self.block_threshold = block_threshold
        self.review_threshold = review_threshold

    def fuse(self, layer_scores: LayerScores, matches: dict) -> dict:
        """
        Fuse layer scores into a final risk assessment.

        Returns:
            dict with attack_type, risk_level, risk_score, confidence,
                 should_block, should_review, explanation
        """
        # Determine dominant attack type
        dominant_attack = _detect_dominant_attack(matches)

        # Choose weights
        weights = ATTACK_WEIGHTS.get(dominant_attack, DEFAULT_WEIGHTS)

        # Weighted average
        risk_score = (
            weights["rules"] * layer_scores.rules
            + weights["fuzzy"] * layer_scores.fuzzy
            + weights["obfuscation"] * layer_scores.obfuscation
            + weights["semantic"] * layer_scores.semantic
            + weights["transformer"] * layer_scores.transformer
            + weights["language_penalty"] * layer_scores.language_penalty
        )
        # Boost risk score if a high-confidence attack signature is detected
        if layer_scores.rules >= 0.80 or (layer_scores.rules >= 0.60 and layer_scores.semantic >= 0.60):
            risk_score = max(risk_score, 0.88)
        elif layer_scores.rules >= 0.65 and dominant_attack in (
            AttackType.DIRECT_INJECTION,
            AttackType.JAILBREAK,
            AttackType.DATA_EXFILTRATION,
            AttackType.SYSTEM_PROMPT_EXTRACTION,
        ):
            risk_score = max(risk_score, 0.85)

        risk_score = min(max(risk_score, 0.0), 1.0)

        # Confidence (derived from evidence richness)
        evidence_count = (
            len(matches.get("rule_matches", []))
            + len(matches.get("fuzzy_matches", []))
            + len(matches.get("semantic_matches", []))
            + len(matches.get("obfuscation_flags", []))
        )
        confidence = min(0.50 + evidence_count * 0.08, 0.95)

        # Final attack type
        final_attack = dominant_attack if risk_score >= 0.30 else AttackType.SAFE
        risk_level = RiskLevel.from_score(risk_score)

        # Actions
        should_block = risk_score >= self.block_threshold
        should_review = self.review_threshold <= risk_score < self.block_threshold

        # Explanation
        parts = []
        if layer_scores.rules > 0.3:
            parts.append(f"Regex patterns matched (score: {layer_scores.rules:.2f})")
        if layer_scores.fuzzy > 0.3:
            parts.append(f"Fuzzy similarity to known attacks (score: {layer_scores.fuzzy:.2f})")
        if layer_scores.obfuscation > 0.3:
            parts.append(f"Obfuscation techniques detected (score: {layer_scores.obfuscation:.2f})")
        if layer_scores.semantic > 0.3:
            parts.append(f"Semantic similarity to attack patterns (score: {layer_scores.semantic:.2f})")
        if layer_scores.transformer > 0.3:
            parts.append(f"Transformer classifier flagged (score: {layer_scores.transformer:.2f})")
        if not parts:
            parts.append("No significant threat signals detected.")

        explanation = f"Risk assessment: {risk_level.value} ({risk_score:.2f}). " + " | ".join(parts)

        return {
            "attack_type": final_attack,
            "risk_level": risk_level,
            "risk_score": round(risk_score, 4),
            "confidence": round(confidence, 4),
            "should_block": should_block,
            "should_review": should_review,
            "explanation": explanation,
            "weights_used": weights,
        }


# Singleton
fusion_engine = RiskFusionEngine()
