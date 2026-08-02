import math
import re
from collections import defaultdict
from typing import List, Dict, Any, Optional
from app.retrieval.base import BaseRetriever
from app.retrieval.models import RetrievalResult


def default_tokenizer(text: str) -> List[str]:
    """
    Simple whitespace and alphanumeric tokenizer.
    """
    return re.findall(r"\w+", text.lower())


class BM25Retriever(BaseRetriever):
    """
    BM25 lexical search retriever built from scratch using Okapi BM25 ranking algorithm.
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        tokenizer=None,
    ):
        self.k1 = k1
        self.b = b
        self.tokenizer = tokenizer or default_tokenizer
        
        self.doc_count: int = 0
        self.avgdl: float = 0.0
        self.doc_lengths: List[int] = []
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.corpus_chunks: List[Dict[str, Any]] = []

    def index(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Index a list of chunk dictionaries.
        Each chunk dict should have: 'chunk_id', 'doc_id', 'content', and optional 'metadata'.
        """
        self.corpus_chunks = chunks
        self.doc_count = len(chunks)
        self.doc_lengths = []
        self.doc_term_freqs = []
        df: Dict[str, int] = defaultdict(int)

        total_length = 0
        for chunk in chunks:
            content = chunk.get("content") or chunk.get("text") or ""
            tokens = self.tokenizer(content)
            length = len(tokens)
            self.doc_lengths.append(length)
            total_length += length

            tf: Dict[str, int] = defaultdict(int)
            for token in tokens:
                tf[token] += 1
            self.doc_term_freqs.append(tf)

            for token in tf.keys():
                df[token] += 1

        self.avgdl = (total_length / self.doc_count) if self.doc_count > 0 else 0.0

        # Calculate Okapi BM25 IDF for each term
        self.idf = {}
        for token, doc_freq in df.items():
            # Standard Okapi BM25 IDF formula with smoothing to avoid negative IDF values
            idf_val = math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
            self.idf[token] = idf_val

    def _auto_load_chunks(self) -> None:
        """
        Attempts to automatically load and index data/processed/chunks.json if available.
        """
        import json
        from pathlib import Path
        base_path = Path(__file__).resolve().parent.parent.parent
        possible_paths = [
            Path("data/processed/chunks.json"),
            base_path / "data" / "processed" / "chunks.json",
            base_path.parent / "data" / "processed" / "chunks.json",
        ]
        for p in possible_paths:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        chunks = json.load(f)
                    if isinstance(chunks, list) and chunks:
                        self.index(chunks)
                        break
                except Exception:
                    pass

    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Calculates BM25 relevance scores for the query against indexed corpus.
        """
        if self.doc_count == 0:
            self._auto_load_chunks()

        if not query.strip() or self.doc_count == 0:
            return []

        query_tokens = self.tokenizer(query)
        scores: List[float] = [0.0] * self.doc_count

        for i in range(self.doc_count):
            doc_len = self.doc_lengths[i]
            tf_dict = self.doc_term_freqs[i]
            score = 0.0

            for token in query_tokens:
                if token not in tf_dict:
                    continue
                
                freq = tf_dict[token]
                idf_val = self.idf.get(token, 0.0)
                
                # BM25 term score formula
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                score += idf_val * (numerator / denominator)

            scores[i] = score

        # Rank document indices by score descending
        ranked_indices = sorted(
            range(self.doc_count),
            key=lambda i: scores[i],
            reverse=True,
        )

        results: List[RetrievalResult] = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] <= 0.0 and len(results) > 0:
                pass

            chunk = self.corpus_chunks[idx]
            chunk_id = chunk.get("chunk_id") or chunk.get("id") or f"bm25-{idx}"
            content = chunk.get("content") or chunk.get("text") or ""
            
            metadata = chunk.get("metadata") or {}
            if not metadata:
                metadata = {
                    "episode_id": chunk.get("episode_id", ""),
                    "guest": chunk.get("guest", ""),
                    "title": chunk.get("title", ""),
                    "topics": chunk.get("topics", ""),
                    "publish_date": chunk.get("publish_date", ""),
                    "youtube_url": chunk.get("youtube_url", ""),
                    "chunk_number": chunk.get("chunk_number", 0),
                }

            results.append(
                RetrievalResult(
                    doc_id=chunk.get("doc_id") or chunk.get("episode_id") or chunk_id,
                    chunk_id=chunk_id,
                    content=content,
                    score=scores[idx],
                    metadata=metadata,
                )
            )

        return results
