import asyncio
from typing import List, Optional
from app.retrieval.base import BaseRetriever
from app.retrieval.models import RetrievalResult
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.rrf import reciprocal_rank_fusion


class HybridRetriever(BaseRetriever):
    """
    Hybrid retriever that combines Dense (Vector) and Sparse (BM25) search using RRF.
    """

    def __init__(
        self,
        dense_retriever: Optional[DenseRetriever] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
        rrf_k: int = 60,
    ):
        self.dense_retriever = dense_retriever or DenseRetriever()
        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.rrf_k = rrf_k

    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Executes Dense and BM25 retrievers asynchronously and fuses results using RRF.
        """
        if not query.strip():
            return []

        # Fetch top_k candidate items from each retriever in parallel
        dense_task = self.dense_retriever.retrieve(query, top_k=top_k)
        bm25_task = self.bm25_retriever.retrieve(query, top_k=top_k)

        dense_results, bm25_results = await asyncio.gather(dense_task, bm25_task)

        # Fuse results with Reciprocal Rank Fusion
        fused_results = reciprocal_rank_fusion(
            retrieval_runs=[dense_results, bm25_results],
            k=self.rrf_k,
            top_k=top_k,
        )

        return fused_results
