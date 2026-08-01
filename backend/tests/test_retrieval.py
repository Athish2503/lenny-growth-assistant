import pytest
import asyncio
from typing import List, Dict, Any
from app.retrieval import (
    RetrievalResult,
    BaseRetriever,
    Retriever,
    DenseRetriever,
    BM25Retriever,
    HybridRetriever,
    reciprocal_rank_fusion,
)


class MockDenseRetriever(BaseRetriever):
    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        return [
            RetrievalResult(doc_id="doc1", chunk_id="c1", content="Growth metrics and retention strategies", score=0.9, metadata={"guest": "Lenny"}),
            RetrievalResult(doc_id="doc2", chunk_id="c2", content="Product market fit indicators", score=0.8, metadata={"guest": "Brian"}),
        ][:top_k]


def test_bm25_retriever():
    async def _test():
        chunks = [
            {"doc_id": "doc1", "chunk_id": "c1", "content": "growth strategy for early stage startups", "metadata": {"category": "growth"}},
            {"doc_id": "doc2", "chunk_id": "c2", "content": "user acquisition tactics and virality", "metadata": {"category": "marketing"}},
            {"doc_id": "doc3", "chunk_id": "c3", "content": "product management frameworks for teams", "metadata": {"category": "pm"}},
        ]
        bm25 = BM25Retriever()
        bm25.index(chunks)

        results = await bm25.retrieve("startups growth", top_k=2)
        assert len(results) == 1 or len(results) == 2
        assert results[0].chunk_id == "c1"
        assert results[0].score > 0
        assert results[0].metadata["category"] == "growth"

    asyncio.run(_test())


def test_rrf():
    run1 = [
        RetrievalResult(doc_id="doc1", chunk_id="c1", content="Text A", score=0.9),
        RetrievalResult(doc_id="doc2", chunk_id="c2", content="Text B", score=0.8),
    ]
    run2 = [
        RetrievalResult(doc_id="doc2", chunk_id="c2", content="Text B", score=0.95),
        RetrievalResult(doc_id="doc1", chunk_id="c1", content="Text A", score=0.85),
    ]

    fused = reciprocal_rank_fusion([run1, run2], k=60, top_k=2)
    assert len(fused) == 2
    assert fused[0].score == fused[1].score


def test_hybrid_retriever():
    async def _test():
        chunks = [
            {"doc_id": "doc1", "chunk_id": "c1", "content": "Growth metrics and retention strategies", "metadata": {"guest": "Lenny"}},
            {"doc_id": "doc2", "chunk_id": "c2", "content": "Product market fit indicators", "metadata": {"guest": "Brian"}},
        ]
        bm25 = BM25Retriever()
        bm25.index(chunks)

        dense = MockDenseRetriever()
        hybrid = HybridRetriever(dense_retriever=dense, bm25_retriever=bm25, rrf_k=60)

        results = await hybrid.retrieve("Growth metrics", top_k=2)
        assert len(results) == 2
        assert isinstance(results[0], RetrievalResult)
        assert results[0].score > 0

    asyncio.run(_test())

