import tempfile
import pytest
from pathlib import Path

from app.ingestion.models import Chunk
from app.ingestion.storage import Storage
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_store import VectorStore
from app.repositories.vector_repository import VectorRepository


@pytest.mark.anyio
async def test_embedding_service():
    service = EmbeddingService(model_name="all-MiniLM-L6-v2")
    text = "Growth assistant product management tips."
    embedding = await service.embed_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert isinstance(float(embedding[0]), float)

    texts = ["First chunk content.", "Second chunk content."]
    embeddings = await service.embed_documents(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == len(embedding)


@pytest.mark.anyio
async def test_vector_repository_add_chunks():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        vector_store = VectorStore(
            persist_directory=tmp_dir,
            collection_name="test_collection"
        )
        embedding_service = EmbeddingService()
        repo = VectorRepository(
            vector_store=vector_store,
            embedding_service=embedding_service
        )

        chunks = [
            Chunk(
                chunk_id="c1",
                doc_id="d1",
                content="Lenny's Newsletter podcast transcript chunk 1",
                chunk_index=0,
                metadata={"speaker": "Lenny"}
            ),
            Chunk(
                chunk_id="c2",
                doc_id="d1",
                content="Lenny's Newsletter podcast transcript chunk 2",
                chunk_index=1,
                metadata={"speaker": "Guest"}
            )
        ]

        await repo.add_chunks(chunks)

        collection = await vector_store.get_collection()
        count = await collection.count()
        assert count == 2


@pytest.mark.anyio
async def test_vector_repository_add_chunks_from_file():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        tmp_path = Path(tmp_dir)
        json_file = tmp_path / "chunks.json"

        chunks = [
            Chunk(
                chunk_id="c_file_1",
                doc_id="d_file_1",
                content="Product strategy chunk from file",
                chunk_index=0,
                metadata={"category": "Strategy"}
            )
        ]
        Storage.save_chunks_to_json(chunks, json_file)

        vector_store = VectorStore(
            persist_directory=str(tmp_path / "chroma_db"),
            collection_name="test_file_collection"
        )
        repo = VectorRepository(vector_store=vector_store)

        await repo.add_chunks_from_file(json_file)

        collection = await vector_store.get_collection()
        count = await collection.count()
        assert count == 1
