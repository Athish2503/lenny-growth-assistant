import json
import math
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

from app.retrieval.config import RetrievalConfig
from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.retrieval.index_pipeline import IndexPipeline


class TestEmbeddingService:
    """Unit tests for EmbeddingService."""

    @patch("app.retrieval.embedding_service.SentenceTransformer")
    def test_embedding_service_init_and_embed(self, mock_transformer_cls):
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        # Return mock normalized vector
        dummy_vec = np.ones((2, 384), dtype=np.float32) / np.sqrt(384)
        mock_model.encode.return_value = dummy_vec
        mock_transformer_cls.return_value = mock_model

        config = RetrievalConfig(EMBEDDING_MODEL="all-MiniLM-L6-v2", BATCH_SIZE=2, DEVICE="cpu")
        service = EmbeddingService(config=config)

        assert service.embedding_dimension == 384
        mock_transformer_cls.assert_called_once_with("all-MiniLM-L6-v2", device="cpu")

        # Test embed_documents
        texts = ["Hello world", "RAG indexing"]
        docs_embeddings = service.embed_documents(texts)
        assert len(docs_embeddings) == 2
        assert len(docs_embeddings[0]) == 384

    @patch("app.retrieval.embedding_service.SentenceTransformer")
    def test_embed_query(self, mock_transformer_cls):
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        dummy_vec = np.ones((384,), dtype=np.float32) / np.sqrt(384)
        mock_model.encode.return_value = dummy_vec
        mock_transformer_cls.return_value = mock_model

        service = EmbeddingService()
        query_vec = service.embed_query("growth strategies")

        assert len(query_vec) == 384
        assert isinstance(query_vec, list)
        assert isinstance(query_vec[0], float)


class TestVectorStore:
    """Unit tests for VectorStore using temporary directory."""

    def test_vector_store_crud_operations(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
            config = RetrievalConfig(
                CHROMA_DB_PATH=tmp_dir,
                CHROMA_COLLECTION="test_lenny_transcripts",
                CHROMA_API_KEY="",
            )
            store = VectorStore(config=config)

            # 1. Collection creation
            assert store.count() == 0

            # 2. Add documents
            ids = ["chunk-1", "chunk-2"]
            embeddings = [
                [0.1] * 384,
                [-0.2] * 384,
            ]
            documents = ["Text for chunk 1", "Text for chunk 2"]
            metadatas = [
                {"guest": "Ada", "chunk_number": 1, "topics": "Coaching"},
                {"guest": "Lenny", "chunk_number": 2, "topics": "Growth"},
            ]

            store.add_documents(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

            assert store.count() == 2

            # 3. Peek
            peek_res = store.peek(limit=1)
            assert len(peek_res["ids"]) == 1

            # 4. Query
            query_res = store.query(query_embeddings=[0.1] * 384, n_results=1)
            assert len(query_res["ids"][0]) == 1
            assert query_res["ids"][0][0] == "chunk-1"

            # 5. Reset collection / Delete
            store.reset_collection()
            assert store.count() == 0
            store.delete_collection()


class TestIndexPipeline:
    """Unit tests for IndexPipeline."""

    def test_prepare_metadata(self):
        pipeline = IndexPipeline(
            embedding_service=MagicMock(),
            vector_store=MagicMock(),
        )

        raw_chunk = {
            "id": "c123",
            "episode_id": "ep1",
            "chunk_number": 5,
            "guest": "Shreyas Doshi",
            "title": "Product Leadership",
            "topics": ["Strategy", "Execution"],
            "publish_date": "2023-01-01",
            "youtube_url": "https://youtube.com/watch?v=123",
            "text": "Sample transcript snippet",
        }

        meta = pipeline.prepare_metadata(raw_chunk)
        assert meta["guest"] == "Shreyas Doshi"
        assert meta["topics"] == "Strategy, Execution"
        assert meta["chunk_number"] == 5

    def test_duplicate_protection_and_indexing_flow(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
            tmp_path = Path(tmp_dir)
            chunks_json = tmp_path / "chunks.json"

            sample_chunks = [
                {
                    "id": "chunk-101",
                    "episode_id": "ep-1",
                    "chunk_number": 1,
                    "guest": "Guest A",
                    "title": "Title A",
                    "topics": ["Topic1"],
                    "publish_date": "2023-01-01",
                    "youtube_url": "http://yt.com/1",
                    "text": "First chunk text content.",
                },
                {
                    "id": "chunk-102",
                    "episode_id": "ep-1",
                    "chunk_number": 2,
                    "guest": "Guest A",
                    "title": "Title A",
                    "topics": ["Topic2"],
                    "publish_date": "2023-01-01",
                    "youtube_url": "http://yt.com/1",
                    "text": "Second chunk text content.",
                },
            ]

            with open(chunks_json, "w", encoding="utf-8") as f:
                json.dump(sample_chunks, f)

            config = RetrievalConfig(
                CHROMA_PATH=str(tmp_path / "chroma_db"),
                COLLECTION_NAME="test_pipeline_coll",
                CHUNKS_FILE_PATH=str(chunks_json),
                BATCH_SIZE=2,
                CHROMA_API_KEY="",
            )

            # Mock EmbeddingService to avoid downloading weights during fast unit tests
            mock_embedding_service = MagicMock()
            mock_embedding_service.embedding_dimension = 384
            mock_embedding_service.embed.return_value = [
                [0.05] * 384,
                [0.10] * 384,
            ]

            vector_store = VectorStore(config=config)
            pipeline = IndexPipeline(
                embedding_service=mock_embedding_service,
                vector_store=vector_store,
                config=config,
            )

            # First run: should index 2 chunks
            res1 = pipeline.run(chunks_path=chunks_json)
            assert res1["documents_indexed"] == 2
            assert res1["collection_size"] == 2

            # Second run: duplicate protection should skip both chunks
            res2 = pipeline.run(chunks_path=chunks_json)
            assert res2["documents_indexed"] == 0
            assert res2["collection_size"] == 2
