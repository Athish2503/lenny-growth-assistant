import asyncio
from typing import List, Optional
from app.retrieval.base import BaseRetriever
from app.retrieval.models import RetrievalResult
from app.repositories.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService


class DenseRetriever(BaseRetriever):
    """
    Vector similarity retriever using ChromaDB and embedding models.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService()

    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Embeds the query and searches ChromaDB vector store for top_k nearest neighbors.
        """
        if not query.strip():
            return []

        # 1. Embed query
        query_embedding = await self.embedding_service.embed_query(query)

        # 2. Query ChromaDB collection
        chroma_response = await self.vector_store.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        results: List[RetrievalResult] = []

        ids = chroma_response.get("ids", [[]])[0]
        documents = chroma_response.get("documents", [[]])[0]
        metadatas = chroma_response.get("metadatas", [[]])[0]
        distances = chroma_response.get("distances", [[]])[0]

        for chunk_id, doc_text, meta, dist in zip(ids, documents, metadatas, distances):
            metadata_dict = dict(meta) if meta else {}
            doc_id = str(metadata_dict.pop("doc_id", chunk_id))
            
            # ChromaDB returns distance (lower is better, e.g. L2 distance or cosine distance)
            # Similarity score = 1 / (1 + distance) or cosine similarity (1 - distance)
            score = 1.0 / (1.0 + float(dist)) if dist is not None else 0.0

            results.append(
                RetrievalResult(
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    content=doc_text,
                    score=score,
                    metadata=metadata_dict,
                )
            )

        return results
