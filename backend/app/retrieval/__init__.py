from app.retrieval.models import RetrievalResult
from app.retrieval.base import BaseRetriever
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.rrf import reciprocal_rank_fusion
from app.retrieval.hybrid_retriever import HybridRetriever

# Alias Retriever to BaseRetriever to satisfy requirement
Retriever = BaseRetriever

__all__ = [
    "RetrievalResult",
    "BaseRetriever",
    "Retriever",
    "DenseRetriever",
    "BM25Retriever",
    "reciprocal_rank_fusion",
    "HybridRetriever",
]
