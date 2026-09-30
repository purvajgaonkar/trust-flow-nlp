"""
Evidence Retrieval module.
Searches vector stores for relevant factual evidence to corroborate claims.
"""

from typing import List, Dict, Any
from app.retrieval.vector_store import vector_store
from app.retrieval.reranker import reranker

def retrieve_claim_evidence(claim_text: str, top_k: int = 3, threshold: float = 0.3) -> List[Dict[str, Any]]:
    """
    Retrieve and rerank corroborating evidence candidates for a claim.
    """
    candidates = vector_store.search(claim_text, top_k=top_k * 2)
    reranked = reranker.rerank(claim_text, candidates, top_k=top_k)
    
    # Filter by minimum relevance threshold
    results = []
    for doc in reranked:
        score = doc.get("rerank_score", doc.get("similarity", 0.0))
        if score >= threshold:
            results.append({
                "id": doc.get("id", ""),
                "text": doc.get("text", ""),
                "source": doc.get("source", "Knowledge Base"),
                "similarity": round(float(score), 4),
            })
    return results
