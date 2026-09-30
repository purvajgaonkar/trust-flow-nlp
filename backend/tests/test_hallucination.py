"""
Hallucination tests for Trust Flow backend.
Supports both pytest and standard unittest runner.
"""

import unittest
from app.hallucination.analyzer import extract_claims, retrieve_evidence, run_nli, score_hallucination, hallucination_analyzer


class TestClaimExtraction(unittest.TestCase):
    def test_single_sentence_claim(self):
        text = "Tesla was founded in 2003."
        claims = extract_claims(text)
        self.assertGreaterEqual(len(claims), 1)
        self.assertEqual(claims[0]["text"], "Tesla was founded in 2003.")

    def test_multiple_sentences(self):
        text = "Einstein was born in Germany. He developed the theory of relativity. He won the Nobel Prize."
        claims = extract_claims(text)
        self.assertGreaterEqual(len(claims), 2)

    def test_claim_has_required_fields(self):
        text = "Python was created by Guido van Rossum."
        claims = extract_claims(text)
        self.assertGreater(len(claims), 0)
        claim = claims[0]
        self.assertIn("id", claim)
        self.assertIn("text", claim)
        self.assertIn("entities", claim)
        self.assertIn("relations", claim)

    def test_empty_text(self):
        claims = extract_claims("")
        self.assertEqual(len(claims), 0)


class TestEvidenceRetrieval(unittest.TestCase):
    def test_returns_results(self):
        evidence = retrieve_evidence("Tesla founded", top_k=3)
        self.assertIsInstance(evidence, list)
        self.assertLessEqual(len(evidence), 3)

    def test_relevance_scores_normalized(self):
        evidence = retrieve_evidence("Albert Einstein Nobel Prize", top_k=3)
        for ev in evidence:
            self.assertGreaterEqual(ev["relevance_score"], 0.0)
            self.assertLessEqual(ev["relevance_score"], 1.0)

    def test_evidence_has_required_fields(self):
        evidence = retrieve_evidence("Tesla", top_k=2)
        if evidence:
            ev = evidence[0]
            self.assertIn("id", ev)
            self.assertIn("text", ev)
            self.assertIn("source", ev)
            self.assertIn("relevance_score", ev)


class TestNLI(unittest.TestCase):
    def test_entailment_returns_valid_result(self):
        result = run_nli(
            "Tesla was founded in 2003 by Martin Eberhard.",
            "Tesla was founded in 2003."
        )
        self.assertIn(result["label"], ["ENTAILMENT", "CONTRADICTION", "NEUTRAL"])
        self.assertGreaterEqual(result["entailment_score"], 0.0)
        self.assertLessEqual(result["entailment_score"], 1.0)
        self.assertGreaterEqual(result["contradiction_score"], 0.0)
        self.assertLessEqual(result["contradiction_score"], 1.0)
        self.assertGreaterEqual(result["neutral_score"], 0.0)
        self.assertLessEqual(result["neutral_score"], 1.0)
        self.assertIn("model_name", result)
        self.assertIn("is_mock", result)

    def test_scores_sum_approximately_one(self):
        result = run_nli("Water boils at 100°C.", "Water boils at 100 degrees.")
        total = result["entailment_score"] + result["contradiction_score"] + result["neutral_score"]
        self.assertLess(abs(total - 1.0), 0.15)


class TestHallucinationScoring(unittest.TestCase):
    def test_entailment_lowers_risk(self):
        risk = score_hallucination("ENTAILMENT", 0.8, True)
        self.assertLess(risk, 0.5)

    def test_contradiction_raises_risk(self):
        risk = score_hallucination("CONTRADICTION", 0.2, True)
        self.assertGreater(risk, 0.5)

    def test_no_evidence_raises_risk(self):
        risk_with = score_hallucination("NEUTRAL", 0.5, True)
        risk_without = score_hallucination("NEUTRAL", 0.5, False)
        self.assertGreaterEqual(risk_without, risk_with)

    def test_score_bounded(self):
        for label in ["ENTAILMENT", "CONTRADICTION", "NEUTRAL"]:
            for sim in [0.0, 0.5, 1.0]:
                for has_ev in [True, False]:
                    score = score_hallucination(label, sim, has_ev)
                    self.assertGreaterEqual(score, 0.0)
                    self.assertLessEqual(score, 1.0)


class TestFullHallucinationPipeline(unittest.TestCase):
    def test_accurate_response_low_risk(self):
        response = "Tesla was founded in July 2003 by Martin Eberhard and Marc Tarpenning."
        result = hallucination_analyzer.analyze(response)
        self.assertIn("overall_hallucination_risk", result)
        self.assertGreaterEqual(result["overall_hallucination_risk"], 0.0)
        self.assertLessEqual(result["overall_hallucination_risk"], 1.0)
        self.assertIn("claims", result)
        self.assertIn("key_findings", result)

    def test_empty_response(self):
        result = hallucination_analyzer.analyze(".")
        self.assertIsInstance(result, dict)
        self.assertIn("overall_hallucination_risk", result)


if __name__ == "__main__":
    unittest.main()
