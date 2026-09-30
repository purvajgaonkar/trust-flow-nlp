"""
Layer D – Transformer-based classifier for prompt injection.
Falls back to keyword heuristics when model is unavailable.
Clearly labeled MOCK/DEMONSTRATION where applicable.
"""

import logging
from typing import Dict, Tuple

from app.security.types import AttackType

logger = logging.getLogger(__name__)

# Attack type labels for mock classification
LABEL_MAP = {
    0: AttackType.SAFE,
    1: AttackType.DIRECT_INJECTION,
    2: AttackType.INDIRECT_INJECTION,
    3: AttackType.JAILBREAK,
    4: AttackType.SYSTEM_PROMPT_EXTRACTION,
    5: AttackType.DATA_EXFILTRATION,
    6: AttackType.ROLE_MANIPULATION,
    7: AttackType.OBFUSCATION,
    8: AttackType.MULTILINGUAL_ATTACK,
    9: AttackType.UNKNOWN_ATTACK,
}

# Simple keyword heuristics used when transformer model is not available
KEYWORD_HEURISTICS: Dict[AttackType, list] = {
    AttackType.DIRECT_INJECTION: ["ignore", "override", "disregard", "forget", "new instruction"],
    AttackType.JAILBREAK: ["jailbreak", "dan", "no restrictions", "bypass filter", "unrestricted"],
    AttackType.SYSTEM_PROMPT_EXTRACTION: ["system prompt", "reveal", "show instructions", "initial prompt"],
    AttackType.DATA_EXFILTRATION: ["exfiltrate", "send data", "leak", "expose", "dump"],
    AttackType.ROLE_MANIPULATION: ["you are now", "act as", "pretend", "roleplay as", "you are a"],
    AttackType.OBFUSCATION: ["\u200b", "\u202e", "base64", "&#"],
}


def _keyword_classify(text: str) -> Tuple[AttackType, float, Dict[str, float]]:
    """
    Heuristic classification using keyword counting.
    NOTE: This is a fallback; results are NOT calibrated probabilities.
    """
    text_lower = text.lower()
    scores: Dict[AttackType, float] = {at: 0.0 for at in LABEL_MAP.values()}
    scores[AttackType.SAFE] = 0.5  # Prior

    for attack_type, keywords in KEYWORD_HEURISTICS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits:
            scores[attack_type] = min(0.3 + hits * 0.15, 0.85)
            scores[AttackType.SAFE] -= hits * 0.05

    scores[AttackType.SAFE] = max(0.05, scores[AttackType.SAFE])

    # Normalize
    total = sum(scores.values())
    if total > 0:
        scores = {k: v / total for k, v in scores.items()}

    best = max(scores, key=scores.__getitem__)
    return best, scores[best], {k.value: round(v, 4) for k, v in scores.items()}


class TransformerClassifier:
    """
    Layer D: BERT/RoBERTa-based classifier.
    In MOCK MODE (when model unavailable), uses keyword heuristics.
    Results from mock mode are clearly labeled as NOT real ML predictions.
    """

    def __init__(self, model_name: str = "martin-ha/toxic-comment-model"):
        self.model_name = model_name
        self.pipeline = None
        self.is_mock = True
        self._load_model()

    def _load_model(self):
        """
        Attempt to load a real transformer classifier.
        If unavailable, fall back to keyword heuristics (mock mode).
        """
        try:
            from transformers import pipeline as hf_pipeline
            self.pipeline = hf_pipeline(
                "text-classification",
                model=self.model_name,
                top_k=None,
                truncation=True,
                max_length=512,
            )
            self.is_mock = False
            logger.info(f"TransformerClassifier loaded: {self.model_name}")
        except Exception as e:
            logger.warning(
                f"Transformer model unavailable ({e}). "
                "Using keyword heuristics – MOCK/DEMONSTRATION MODE."
            )
            self.is_mock = True

    def classify(self, text: str) -> dict:
        """
        Classify input text.

        Returns dict with:
          - attack_type, confidence, all_scores, model_name, is_mock
        """
        if self.is_mock or self.pipeline is None:
            attack_type, conf, all_scores = _keyword_classify(text)
            return {
                "attack_type": attack_type,
                "confidence": round(conf, 4),
                "all_scores": all_scores,
                "model_name": "keyword-heuristic-fallback",
                "is_mock": True,
            }

        try:
            result = self.pipeline(text[:512])
            # Map model output to our labels (model may have different label schema)
            raw = result[0] if isinstance(result[0], list) else result
            best_label = max(raw, key=lambda x: x["score"])

            # Since we're using a generic model, map to SAFE/UNSAFE broadly
            is_safe = best_label["label"] in ("LABEL_0", "SAFE", "non-toxic", "ham")
            attack_type = AttackType.SAFE if is_safe else AttackType.UNKNOWN_ATTACK
            conf = round(best_label["score"], 4)

            all_scores = {
                AttackType.SAFE.value: conf if is_safe else round(1 - conf, 4),
                AttackType.UNKNOWN_ATTACK.value: round(1 - conf, 4) if is_safe else conf,
            }
            return {
                "attack_type": attack_type,
                "confidence": conf,
                "all_scores": all_scores,
                "model_name": self.model_name,
                "is_mock": False,
            }
        except Exception as e:
            logger.warning(f"Transformer inference failed: {e}. Falling back to mock.")
            attack_type, conf, all_scores = _keyword_classify(text)
            return {
                "attack_type": attack_type,
                "confidence": round(conf, 4),
                "all_scores": all_scores,
                "model_name": "keyword-heuristic-fallback",
                "is_mock": True,
            }


# Singleton
transformer_classifier = TransformerClassifier()
