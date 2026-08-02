import sys
from pathlib import Path

_backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

"""
app.retrieval — Public surface of the retrieval + ingestion package.

Ingestion pipeline exports:
    TranscriptLoader, TranscriptParser, TopicParser,
    TranscriptCleaner, SemanticChunker, IngestionPipeline

Retrieval algorithm exports:
    BaseRetriever, DenseRetriever, BM25Retriever,
    HybridRetriever, reciprocal_rank_fusion

Embedding & Indexing exports:
    RetrievalConfig, get_retrieval_config,
    EmbeddingService, VectorStore, IndexPipeline

Shared model exports:
    RetrievalResult, Document, Chunk, TopicMap, EpisodeMetadata
"""

from .models import (
    RetrievalResult,
    Document,
    Chunk,
    TopicMap,
    EpisodeMetadata,
)

# Ingestion pipeline components
from .loader import TranscriptLoader
from .parser import TranscriptParser
from .topic_parser import TopicParser
from .cleaner import TranscriptCleaner
from .chunker import SemanticChunker
from .pipeline import IngestionPipeline

# Retrieval algorithm components
from .base import BaseRetriever
from .dense_retriever import DenseRetriever
from .bm25_retriever import BM25Retriever
from .rrf import reciprocal_rank_fusion
from .hybrid_retriever import HybridRetriever

# Embedding & Indexing components
from .config import RetrievalConfig, get_retrieval_config
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from .index_pipeline import IndexPipeline

# Alias kept for backwards compatibility
Retriever = BaseRetriever

__all__ = [
    # Models
    "RetrievalResult",
    "Document",
    "Chunk",
    "TopicMap",
    "EpisodeMetadata",
    # Ingestion pipeline
    "TranscriptLoader",
    "TranscriptParser",
    "TopicParser",
    "TranscriptCleaner",
    "SemanticChunker",
    "IngestionPipeline",
    # Retrieval algorithms
    "BaseRetriever",
    "Retriever",
    "DenseRetriever",
    "BM25Retriever",
    "reciprocal_rank_fusion",
    "HybridRetriever",
    # Embedding & Indexing
    "RetrievalConfig",
    "get_retrieval_config",
    "EmbeddingService",
    "VectorStore",
    "IndexPipeline",
]
