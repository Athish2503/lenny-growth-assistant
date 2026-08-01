from typing import List, Dict, Tuple
from app.retrieval.models import RetrievalResult


def reciprocal_rank_fusion(
    retrieval_runs: List[List[RetrievalResult]],
    k: int = 60,
    top_k: int = 5,
) -> List[RetrievalResult]:
    """
    Combines ranked lists from multiple retrievers using Reciprocal Rank Fusion (RRF).

    RRF score for doc d: sum_{r in runs} 1 / (k + rank(r, d))

    Args:
        retrieval_runs: List of ranked RetrievalResult lists from different retrievers.
        k: Constant ranking parameter (default 60).
        top_k: Number of combined results to return.

    Returns:
        Combined list of top_k RetrievalResult items sorted by fused RRF score.
    """
    rrf_scores: Dict[str, float] = {}
    doc_map: Dict[str, RetrievalResult] = {}

    for run in retrieval_runs:
        for rank, result in enumerate(run, start=1):
            chunk_id = result.chunk_id
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0
                doc_map[chunk_id] = result
            
            rrf_scores[chunk_id] += 1.0 / (k + rank)

    # Sort chunks by RRF score descending
    sorted_chunks = sorted(
        rrf_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    fused_results: List[RetrievalResult] = []
    for chunk_id, fused_score in sorted_chunks[:top_k]:
        original_result = doc_map[chunk_id]
        fused_results.append(
            RetrievalResult(
                doc_id=original_result.doc_id,
                chunk_id=original_result.chunk_id,
                content=original_result.content,
                score=fused_score,
                metadata=original_result.metadata,
            )
        )

    return fused_results
