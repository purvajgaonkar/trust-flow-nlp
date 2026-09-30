"""
Natural Language Inference (NLI) module.
Classifies premise-hypothesis pairs into ENTAILMENT, CONTRADICTION, or NEUTRAL.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class NLIClassifier:
    """
    Evaluates semantic relationship between Premise (Evidence) and Hypothesis (Claim).
    """

    def __init__(self, model_name: str = "roberta-large-mnli"):
        self.model_name = model_name
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import pipeline
            self.pipeline = pipeline("text-classification", model=self.model_name)
            logger.info("Loaded NLI pipeline: %s", self.model_name)
        except Exception as e:
            logger.warning("NLI pipeline not loaded (%s). Using heuristic verification.", e)
            self.pipeline = None

    def infer(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Runs NLI inference on premise vs hypothesis.
        """
        if self.pipeline is not None:
            try:
                input_text = f"{premise} </s></s> {hypothesis}"
                res = self.pipeline(input_text)[0]
                label_map = {"ENTAILMENT": "ENTAILMENT", "CONTRADICTION": "CONTRADICTION", "NEUTRAL": "NEUTRAL"}
                label = label_map.get(res["label"].upper(), "NEUTRAL")
                return {
                    "label": label,
                    "confidence": round(float(res["score"]), 4),
                    "model": self.model_name,
                }
            except Exception as e:
                logger.error("NLI inference error: %s", e)

        # Heuristic inference fallback
        p_lower = premise.lower()
        h_lower = hypothesis.lower()

        # Negation / contradiction check
        negations = ["not", "never", "didn't", "wasn't", "incorrect", "false", "unlike"]
        has_negation_diff = any(neg in p_lower for neg in negations) != any(neg in h_lower for neg in negations)

        # Numbers / Year check
        import re
        p_nums = set(re.findall(r"\b\d{4}\b|\b\d+(?:\.\d+)?\b", p_lower))
        h_nums = set(re.findall(r"\b\d{4}\b|\b\d+(?:\.\d+)?\b", h_lower))

        if h_nums and p_nums and not h_nums.issubset(p_nums) and len(p_nums.intersection(h_nums)) == 0:
            return {
                "label": "CONTRADICTION",
                "confidence": 0.88,
                "reason": "Numerical/date mismatch detected between claim and source evidence",
                "model": "heuristic-nli",
            }

        if has_negation_diff:
            return {
                "label": "CONTRADICTION",
                "confidence": 0.75,
                "reason": "Direct negation detected between evidence and claim statement",
                "model": "heuristic-nli",
            }

        # Lexical entity overlap
        h_words = set(re.findall(r"\w+", h_lower)) - {"the", "a", "an", "is", "was", "in", "by", "of", "and"}
        p_words = set(re.findall(r"\w+", p_lower))
        overlap = len(h_words.intersection(p_words)) / max(1, len(h_words))

        if overlap >= 0.65:
            return {
                "label": "ENTAILMENT",
                "confidence": round(min(0.95, 0.5 + overlap * 0.45), 4),
                "reason": "High factual overlap with corroborating source",
                "model": "heuristic-nli",
            }

        return {
            "label": "NEUTRAL",
            "confidence": 0.55,
            "reason": "Insufficient evidence overlap to confirm or contradict claim",
            "model": "heuristic-nli",
        }

nli_classifier = NLIClassifier()
