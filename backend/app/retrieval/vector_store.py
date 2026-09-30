"""
FAISS Vector Store implementation with in-memory fallback.
Stores documents, computes embeddings, and performs fast nearest neighbor retrieval.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np

from app.nlp.embeddings.models import embedding_service

logger = logging.getLogger(__name__)

class VectorStore:
    """
    FAISS-backed vector store for evidence retrieval.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.documents: List[Dict[str, Any]] = []
        self.index = None
        self.use_faiss = False
        self._init_index()

    def _init_index(self):
        try:
            import faiss
            self.index = faiss.IndexFlatIP(self.dimension)
            self.use_faiss = True
            logger.info("Initialized FAISS IndexFlatIP (dim=%d)", self.dimension)
        except Exception as e:
            logger.warning("FAISS not available (%s), falling back to numpy cosine retrieval", e)
            self.use_faiss = False

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        Add documents to store: [{ "id": ..., "text": ..., "source": ... }]
        """
        if not docs:
            return

        texts = [d["text"] for d in docs]
        vectors = embedding_service.encode(texts, dimension=self.dimension)

        if self.use_faiss and self.index is not None:
            self.index.add(vectors.astype(np.float32))

        for doc, vec in zip(docs, vectors):
            doc_copy = dict(doc)
            doc_copy["vector"] = vec
            self.documents.append(doc_copy)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve top_k documents most semantically similar to query.
        """
        if not self.documents:
            return []

        query_vec = embedding_service.encode([query], dimension=self.dimension)[0]

        if self.use_faiss and self.index is not None and self.index.ntotal > 0:
            scores, indices = self.index.search(query_vec.reshape(1, -1).astype(np.float32), min(top_k, len(self.documents)))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents) and idx >= 0:
                    doc = dict(self.documents[idx])
                    doc.pop("vector", None)
                    doc["similarity"] = float(score)
                    results.append(doc)
            return results

        # Fallback numpy search
        scored_docs = []
        for doc in self.documents:
            sim = embedding_service.cosine_similarity(query_vec, doc["vector"])
            doc_res = {k: v for k, v in doc.items() if k != "vector"}
            doc_res["similarity"] = float(sim)
            scored_docs.append(doc_res)

        scored_docs.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_docs[:top_k]

# Global store initialized with built-in knowledge base
vector_store = VectorStore()
