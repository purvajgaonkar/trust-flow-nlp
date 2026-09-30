"""
Hallucination Pipeline – claim extraction, evidence retrieval, NLI scoring.
"""

import re
import time
import uuid
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Built-in Knowledge Base (Wikipedia-style snippets for demo)
# ─────────────────────────────────────────────────────────────────────────────

KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "text": "Tesla, Inc. was founded in July 2003 by Martin Eberhard and Marc Tarpenning. Elon Musk joined as chairman of the board and led the Series A funding round in 2004, and later became CEO in 2008.",
        "source": "Wikipedia: Tesla, Inc.",
    },
    {
        "id": "kb_002",
        "text": "The Eiffel Tower is located in Paris, France. It was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair. It stands 330 metres (1,083 ft) tall.",
        "source": "Wikipedia: Eiffel Tower",
    },
    {
        "id": "kb_003",
        "text": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability. Python was created by Guido van Rossum and first released in 1991.",
        "source": "Wikipedia: Python (programming language)",
    },
    {
        "id": "kb_004",
        "text": "The Great Wall of China is a series of fortifications built across the historical northern borders of ancient Chinese states. The wall was built primarily during the Ming dynasty (1368–1644).",
        "source": "Wikipedia: Great Wall of China",
    },
    {
        "id": "kb_005",
        "text": "Water boils at 100 degrees Celsius (212°F) at standard atmospheric pressure (1 atm). The boiling point decreases with decreasing pressure.",
        "source": "Wikipedia: Boiling point",
    },
    {
        "id": "kb_006",
        "text": "Albert Einstein was born on 14 March 1879 in Ulm, Germany. He developed the theory of special relativity (1905) and general relativity (1915). He received the Nobel Prize in Physics in 1921.",
        "source": "Wikipedia: Albert Einstein",
    },
    {
        "id": "kb_007",
        "text": "The Moon is Earth's only natural satellite. Its average orbital distance is about 384,400 km. The Moon's surface gravity is about 1/6th of Earth's.",
        "source": "Wikipedia: Moon",
    },
    {
        "id": "kb_008",
        "text": "ChatGPT is an AI chatbot developed by OpenAI. It was launched on November 30, 2022. The model is based on GPT-3.5 and later GPT-4.",
        "source": "Wikipedia: ChatGPT",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Claim Extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_claims(text: str) -> List[dict]:
    """
    Break a response into atomic, verifiable claims.
    Uses sentence segmentation + heuristics.
    """
    # Split into sentences (simple approach)
    sentence_pattern = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
    raw_sentences = sentence_pattern.split(text)

    claims = []
    for sent in raw_sentences:
        sent = sent.strip()
        if len(sent) < 10:
            continue

        # Extract simple entities (proper nouns pattern)
        entities = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", sent)

        # Extract relations (subject-verb-object heuristic)
        relations = _extract_relations(sent)

        claims.append({
            "id": f"claim_{uuid.uuid4().hex[:8]}",
            "text": sent,
            "entities": list(set(entities[:5])),
            "relations": relations[:3],
        })

    return claims


def _extract_relations(sentence: str) -> List[dict]:
    """Extract simple SVO triples using regex heuristics."""
    relations = []
    # Pattern: "X was/is/founded Y"
    patterns = [
        (r"(\b[A-Z]\w+\b)\s+(?:was|is|were|are)\s+(?:founded|created|built|established|born)\s+(?:in|by|on)?\s*(\w+)", "FOUNDED_IN"),
        (r"(\b[A-Z]\w+\b)\s+(?:founded|created|built|established)\s+(\b[A-Z]\w+\b)", "FOUNDED"),
        (r"(\b[A-Z]\w+\b)\s+(?:is|was|are|were)\s+(located|situated|based)\s+in\s+(\b[A-Z]\w+\b)", "LOCATED_IN"),
    ]
    for pattern, relation in patterns:
        for m in re.finditer(pattern, sentence):
            if len(m.groups()) >= 2:
                relations.append({
                    "subject": m.group(1),
                    "predicate": relation,
                    "object": m.group(2),
                })
    return relations


# ─────────────────────────────────────────────────────────────────────────────
# Evidence Retrieval (simple cosine with TF-IDF fallback)
# ─────────────────────────────────────────────────────────────────────────────

_RETRIEVAL_MODEL = None
_KB_EMBS = None

def _get_retrieval_model_and_embs():
    global _RETRIEVAL_MODEL, _KB_EMBS
    if _RETRIEVAL_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _RETRIEVAL_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        kb_texts = [e["text"] for e in KNOWLEDGE_BASE]
        _KB_EMBS = _RETRIEVAL_MODEL.encode(kb_texts, convert_to_tensor=True)
    return _RETRIEVAL_MODEL, _KB_EMBS

def retrieve_evidence(claim_text: str, top_k: int = 3) -> List[dict]:
    """
    Retrieve most relevant knowledge base entries for a claim.
    Uses sentence-transformers if available, otherwise keyword overlap.
    """
    try:
        from sentence_transformers import util
        model, kb_embs = _get_retrieval_model_and_embs()
        claim_emb = model.encode(claim_text, convert_to_tensor=True)
        scores = util.cos_sim(claim_emb, kb_embs)[0].cpu().numpy()
        top_indices = scores.argsort()[::-1][:top_k]
        results = []
        for rank, idx in enumerate(top_indices):
            results.append({
                "id": KNOWLEDGE_BASE[idx]["id"],
                "text": KNOWLEDGE_BASE[idx]["text"],
                "source": KNOWLEDGE_BASE[idx]["source"],
                "relevance_score": round(float(scores[idx]), 4),
                "claim_id": "",
                "rank": rank + 1,
            })
        return results
    except Exception:
        pass

    # Keyword overlap fallback
    claim_words = set(claim_text.lower().split())
    scored = []
    for entry in KNOWLEDGE_BASE:
        kb_words = set(entry["text"].lower().split())
        overlap = len(claim_words & kb_words)
        if overlap > 0:
            scored.append((overlap / len(claim_words), entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for rank, (score, entry) in enumerate(scored[:top_k]):
        results.append({
            "id": entry["id"],
            "text": entry["text"],
            "source": entry["source"],
            "relevance_score": round(score, 4),
            "claim_id": "",
            "rank": rank + 1,
        })
    return results

# ─────────────────────────────────────────────────────────────────────────────
# NLI (Natural Language Inference)
# ─────────────────────────────────────────────────────────────────────────────

_NLI_MODEL = None

def _get_nli_model():
    global _NLI_MODEL
    if _NLI_MODEL is None:
        from sentence_transformers import CrossEncoder
        _NLI_MODEL = CrossEncoder("cross-encoder/nli-deberta-v3-small")
    return _NLI_MODEL

def run_nli(premise: str, hypothesis: str) -> dict:
    """
    Run NLI to classify premise → hypothesis relationship.
    Uses CrossEncoder on the [premise, hypothesis] pair.
    """
    try:
        model = _get_nli_model()
        import numpy as np
        scores = model.predict([[premise, hypothesis]])[0]
        # Softmax over logits: CrossEncoder nli-deberta-v3 classes: {0: contradiction, 1: entailment, 2: neutral}
        exp_s = np.exp(scores - np.max(scores))
        probs = exp_s / np.sum(exp_s)
        label_map = {0: "CONTRADICTION", 1: "ENTAILMENT", 2: "NEUTRAL"}
        pred_idx = int(np.argmax(probs))

        # Check for numerical / date contradiction
        p_nums = set(re.findall(r"\b\d{4}\b|\b\d+(?:\.\d+)?\b", premise))
        h_nums = set(re.findall(r"\b\d{4}\b|\b\d+(?:\.\d+)?\b", hypothesis))
        if h_nums and p_nums and not h_nums.issubset(p_nums) and len(p_nums.intersection(h_nums)) == 0:
            pred_idx = 0
            probs[0] = max(probs[0], 0.95)

        return {
            "label": label_map.get(pred_idx, "NEUTRAL"),
            "entailment_score": round(float(probs[1]), 4),
            "contradiction_score": round(float(probs[0]), 4),
            "neutral_score": round(float(probs[2]), 4),
            "model_name": "cross-encoder/nli-deberta-v3-small",
            "is_mock": False,
        }
    except Exception as e:
        logger.warning(f"NLI model error: {e}. Using heuristic.")
        return _heuristic_nli(premise, hypothesis)


def _heuristic_nli(premise: str, hypothesis: str) -> dict:
    """
    Keyword-overlap heuristic for NLI when model unavailable.
    MOCK/DEMONSTRATION MODE – not real NLI predictions.
    """
    p_words = set(premise.lower().split())
    h_words = set(hypothesis.lower().split())
    overlap = len(p_words & h_words)
    ratio = overlap / max(len(h_words), 1)

    # Check for negation
    negations = {"not", "no", "never", "false", "incorrect", "wrong", "doesn't", "isn't", "wasn't"}
    premise_neg = bool(negations & p_words)
    hyp_neg = bool(negations & h_words)
    contradiction_signal = premise_neg != hyp_neg  # One has negation, other doesn't

    if contradiction_signal and ratio > 0.3:
        return {
            "label": "CONTRADICTION",
            "entailment_score": 0.10,
            "contradiction_score": 0.75,
            "neutral_score": 0.15,
            "model_name": "keyword-heuristic-fallback",
            "is_mock": True,
        }
    elif ratio > 0.5:
        return {
            "label": "ENTAILMENT",
            "entailment_score": 0.65,
            "contradiction_score": 0.05,
            "neutral_score": 0.30,
            "model_name": "keyword-heuristic-fallback",
            "is_mock": True,
        }
    else:
        return {
            "label": "NEUTRAL",
            "entailment_score": 0.20,
            "contradiction_score": 0.15,
            "neutral_score": 0.65,
            "model_name": "keyword-heuristic-fallback",
            "is_mock": True,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Semantic Similarity (claim ↔ evidence)
# ─────────────────────────────────────────────────────────────────────────────

def compute_semantic_similarity(text_a: str, text_b: str) -> float:
    """Compute semantic similarity between two texts (0-1)."""
    try:
        from sentence_transformers import util
        model, _ = _get_retrieval_model_and_embs()
        embs = model.encode([text_a, text_b], normalize_embeddings=True)
        return round(float(util.cos_sim(embs[0], embs[1])), 4)
    except Exception:
        # Jaccard fallback
        a_words = set(text_a.lower().split())
        b_words = set(text_b.lower().split())
        union = a_words | b_words
        if not union:
            return 0.0
        return round(len(a_words & b_words) / len(union), 4)
    except Exception:
        # Jaccard fallback
        a_words = set(text_a.lower().split())
        b_words = set(text_b.lower().split())
        union = a_words | b_words
        if not union:
            return 0.0
        return round(len(a_words & b_words) / len(union), 4)


# ─────────────────────────────────────────────────────────────────────────────
# Hallucination Scoring
# ─────────────────────────────────────────────────────────────────────────────

def score_hallucination(nli_label: str, semantic_sim: float, has_evidence: bool) -> float:
    """
    Compute hallucination risk score (0-1) from NLI + evidence + similarity.
    Higher score = higher risk of hallucination.
    """
    if not has_evidence:
        return 0.65

    if nli_label == "CONTRADICTION":
        return 0.88
    elif nli_label == "ENTAILMENT":
        return 0.10 if semantic_sim > 0.40 else 0.25
    else:  # NEUTRAL
        return 0.50


# ─────────────────────────────────────────────────────────────────────────────
# Full Hallucination Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class HallucinationAnalyzer:
    """
    Orchestrates the full hallucination detection pipeline:
    Claim extraction → Evidence retrieval → NLI → Scoring.
    """

    def analyze(self, response_text: str) -> dict:
        """
        Analyze an LLM response for hallucination risk.
        Returns dict compatible with HallucinationResult schema.
        """
        start = time.perf_counter()

        claims_raw = extract_claims(response_text)
        verified_claims = []
        total_hall_risk = 0.0
        supported = contradicted = unverified = 0

        for claim_dict in claims_raw:
            # Retrieve evidence
            evidence_list = retrieve_evidence(claim_dict["text"], top_k=3)
            for ev in evidence_list:
                ev["claim_id"] = claim_dict["id"]

            # NLI against best evidence
            best_ev_text = evidence_list[0]["text"] if evidence_list else ""
            nli_result = run_nli(best_ev_text, claim_dict["text"]) if best_ev_text else {
                "label": "NEUTRAL",
                "entailment_score": 0.0,
                "contradiction_score": 0.0,
                "neutral_score": 1.0,
                "model_name": "no-evidence",
                "is_mock": True,
            }

            # Semantic similarity
            sem_sim = (
                compute_semantic_similarity(best_ev_text, claim_dict["text"])
                if best_ev_text else 0.0
            )

            # Hallucination risk
            hall_risk = score_hallucination(
                nli_result["label"], sem_sim, bool(evidence_list)
            )
            total_hall_risk += hall_risk

            # Count
            if nli_result["label"] == "ENTAILMENT" and sem_sim > 0.5:
                supported += 1
            elif nli_result["label"] == "CONTRADICTION":
                contradicted += 1
            else:
                unverified += 1

            # Explanation
            if nli_result["label"] == "ENTAILMENT":
                explanation = "Evidence supports this claim."
            elif nli_result["label"] == "CONTRADICTION":
                explanation = "Evidence contradicts this claim – possible hallucination."
            else:
                explanation = "Insufficient evidence to verify this claim."

            verified_claims.append({
                "claim": claim_dict,
                "evidence_pieces": evidence_list,
                "nli_result": nli_result,
                "semantic_similarity": sem_sim,
                "hallucination_risk": hall_risk,
                "explanation": explanation,
                "confidence": 0.6 if nli_result.get("is_mock") else 0.85,
            })

        # Aggregate
        n = len(claims_raw) or 1
        overall_risk = round(total_hall_risk / n, 4)
        if contradicted > 0:
            overall_risk = max(overall_risk, 0.78 + min(0.20, (contradicted - 1) * 0.10))
            overall_risk = min(overall_risk, 1.0)

        # Risk level
        from app.security.types import RiskLevel
        risk_level = RiskLevel.from_score(overall_risk)

        # Key findings
        key_findings = []
        if contradicted > 0:
            key_findings.append(f"{contradicted} claim(s) contradict the evidence.")
        if unverified > 0:
            key_findings.append(f"{unverified} claim(s) could not be verified.")
        if supported > 0:
            key_findings.append(f"{supported} claim(s) are supported by evidence.")
        if not key_findings:
            key_findings.append("No verifiable claims found in the response.")

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "overall_hallucination_risk": overall_risk,
            "risk_level": risk_level,
            "total_claims": len(claims_raw),
            "supported_claims": supported,
            "contradicted_claims": contradicted,
            "unverified_claims": unverified,
            "claims": verified_claims,
            "self_consistency": None,
            "explanation": (
                f"Hallucination risk: {risk_level.value} ({overall_risk:.2f}). "
                + " ".join(key_findings)
            ),
            "key_findings": key_findings,
            "processing_time_ms": round(elapsed, 2),
            "is_demo": False,
        }


# Singleton
hallucination_analyzer = HallucinationAnalyzer()
