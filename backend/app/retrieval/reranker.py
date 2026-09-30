"""
Reranking module for cross-encoder retrieval precision enhancement.
Reranks candidate evidence passages against input queries or claims.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Reranks documents using cross-encoder architecture or lexical-semantic fusion.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
            logger.info("Loaded CrossEncoder: %s", self.model_name)
        except Exception as e:
            logger.warning("CrossEncoder not loaded (%s). Using lexical overlap reranking.", e)
            self.model = None

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Rerank a list of documents for a given query/claim.
        """
        if not documents:
            return []

        if self.model is not None:
            try:
                pairs = [[query, doc.get("text", "")] for doc in documents]
                scores = self.model.predict(pairs)
                for doc, score in zip(documents, scores):
                    doc["rerank_score"] = float(score)
                sorted_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
                return sorted_docs[:top_k] if top_k else sorted_docs
            except Exception as e:
                logger.error("Reranking failed: %s", e)

        # Fallback scoring: combines initial vector similarity with exact term matching
        q_terms = set(query.lower().split())
        for doc in documents:
            doc_terms = set(doc.get("text", "").lower().split())
            overlap = len(q_terms.intersection(doc_terms)) / max(1, len(q_terms))
            initial_sim = doc.get("similarity", 0.5)
            doc["rerank_score"] = float(0.6 * initial_sim + 0.4 * overlap)

        sorted_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        return sorted_docs[:top_k] if top_k else sorted_docs

reranker = CrossEncoderReranker()
