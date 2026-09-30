"""
Main Security Analyzer – orchestrates all detection layers.
"""

import time
import logging
from typing import Optional

from app.security.rules import rule_engine
from app.security.fuzzy import fuzzy_detector
from app.security.obfuscation import obfuscation_detector
from app.security.semantic import semantic_detector
from app.security.transformer import transformer_classifier
from app.security.fusion import fusion_engine, LayerScores
from app.security.types import AttackType

logger = logging.getLogger(__name__)

# Language penalty scores (non-English may carry extra risk in certain attack scenarios)
LANGUAGE_PENALTIES = {
    "english": 0.0,
    "hindi": 0.05,
    "marathi": 0.05,
    "hinglish": 0.10,   # Code-mixed – harder to detect
    "unknown": 0.15,
}

# Known attack-specific explainability hints
LIMITATIONS = [
    "Semantic layer requires sentence-transformers; may be disabled if unavailable.",
    "Transformer layer is in MOCK/DEMONSTRATION MODE unless a fine-tuned model is loaded.",
    "Fuzzy matching may produce false positives on legitimate text with common substrings.",
    "Multilingual attacks (non-Latin scripts) may have reduced detection accuracy.",
    "Novel, unseen attack patterns may bypass all detection layers.",
]


class SecurityAnalyzer:
    """
    Orchestrates all four security detection layers + fusion.
    Returns a comprehensive SecurityResult.
    """

    def analyze(self, text: str, language: str = "english") -> dict:
        """
        Run the full 4-layer security pipeline.

        Args:
            text:     Input text to analyze
            language: Detected language

        Returns:
            dict compatible with SecurityResult schema
        """
        start = time.perf_counter()

        # ── Layer A: Rules ─────────────────────────────────────────────────────
        rules_score, rule_matches = rule_engine.analyze(text)

        # ── Layer B: Fuzzy ─────────────────────────────────────────────────────
        fuzzy_score, fuzzy_matches = fuzzy_detector.analyze(text)

        # ── Obfuscation ────────────────────────────────────────────────────────
        obf_score, obf_flags = obfuscation_detector.analyze(text)

        # ── Layer C: Semantic ──────────────────────────────────────────────────
        sem_score, sem_matches = semantic_detector.analyze(text)

        # ── Layer D: Transformer ───────────────────────────────────────────────
        trans_result = transformer_classifier.classify(text)
        trans_score = (
            trans_result["confidence"]
            if trans_result["attack_type"] != AttackType.SAFE
            else 0.0
        )

        # ── Language Penalty ───────────────────────────────────────────────────
        lang_penalty = LANGUAGE_PENALTIES.get(language.lower(), 0.10)

        # ── Fusion ─────────────────────────────────────────────────────────────
        layer_scores = LayerScores(
            rules=rules_score,
            fuzzy=fuzzy_score,
            obfuscation=obf_score,
            semantic=sem_score,
            transformer=trans_score,
            language_penalty=lang_penalty,
        )

        all_matches = {
            "rule_matches": rule_matches,
            "fuzzy_matches": fuzzy_matches,
            "obfuscation_flags": obf_flags,
            "semantic_matches": sem_matches,
            "transformer_prediction": trans_result,
        }

        fusion = fusion_engine.fuse(layer_scores, all_matches)

        elapsed = (time.perf_counter() - start) * 1000

        # ── Build evidence list ────────────────────────────────────────────────
        evidence = []
        for m in rule_matches[:3]:
            evidence.append(f"[Rule] '{m['matched_text']}' matches '{m['pattern_name']}'")
        for m in fuzzy_matches[:2]:
            evidence.append(
                f"[Fuzzy] '{m['matched_text']}' ≈ '{m['target_phrase']}' "
                f"(sim={m['similarity_score']:.2f}, tech={m['technique']})"
            )
        for f in obf_flags[:2]:
            evidence.append(f"[Obfuscation] {f['description']}")
        for m in sem_matches[:2]:
            evidence.append(
                f"[Semantic] Similarity {m['similarity_score']:.2f} to '{m['reference_text'][:60]}...'"
            )
        if trans_result.get("is_mock"):
            evidence.append(
                "[Transformer] MOCK/DEMONSTRATION MODE – keyword heuristic used, not real ML prediction"
            )

        return {
            # Fusion result
            "attack_type": fusion["attack_type"],
            "risk_level": fusion["risk_level"],
            "risk_score": fusion["risk_score"],
            "confidence": fusion["confidence"],
            "should_block": fusion["should_block"],
            "should_review": fusion["should_review"],
            # Layer details
            "layer_scores": {
                "rules_score": round(rules_score, 4),
                "fuzzy_score": round(fuzzy_score, 4),
                "obfuscation_score": round(obf_score, 4),
                "semantic_score": round(sem_score, 4),
                "transformer_score": round(trans_score, 4),
                "language_penalty": round(lang_penalty, 4),
            },
            "rule_matches": rule_matches,
            "fuzzy_matches": fuzzy_matches,
            "obfuscation_flags": obf_flags,
            "semantic_matches": sem_matches,
            "transformer_prediction": trans_result,
            # Explainability
            "explanation": fusion["explanation"],
            "evidence": evidence,
            "limitations": LIMITATIONS,
            # Meta
            "processing_time_ms": round(elapsed, 2),
            "is_demo": False,
        }


# Singleton
security_analyzer = SecurityAnalyzer()
