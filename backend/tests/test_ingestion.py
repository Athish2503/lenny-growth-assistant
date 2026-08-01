import json
import pytest
from pathlib import Path
from app.ingestion import (
    DocumentLoader,
    MetadataExtractor,
    Chunker,
    Storage,
    TranscriptIngestionPipeline,
    Document
)


@pytest.fixture
def sample_markdown_content():
    return """---
guest: Brian Chesky
episode_number: 104
date: "2023-05-15"
---

# Episode 104: Brian Chesky on Building Airbnb

Guest: Brian Chesky

## Introduction to Product Management

Welcome to today's episode with Brian Chesky. We discuss product management, design excellence, and founder-led growth strategies.

## Key Takeaways

1. Stay involved in design details.
2. Focus on core user experiences before scaling.
3. Culture dictates quality.
"""


def test_document_loader_clean(tmp_path, sample_markdown_content):
    file_path = tmp_path / "ep104_brian_chesky.md"
    file_path.write_text(sample_markdown_content + "\r\n\r\n\r\n\r\n", encoding="utf-8")

    loader = DocumentLoader()
    doc = loader.load_file(file_path)

    assert doc.content.startswith("---")
    assert "\r" not in doc.content
    assert "\n\n\n" not in doc.content
    assert doc.source_path == str(file_path.resolve())


def test_metadata_extractor(tmp_path, sample_markdown_content):
    file_path = tmp_path / "ep104_brian_chesky.md"
    file_path.write_text(sample_markdown_content, encoding="utf-8")

    loader = DocumentLoader()
    doc = loader.load_file(file_path)

    extractor = MetadataExtractor()
    meta = extractor.extract_metadata(doc)

    assert meta["guest"] == "Brian Chesky"
    assert meta["episode_number"] == 104
    assert meta["title"] == "Episode 104: Brian Chesky on Building Airbnb"


def test_chunker(tmp_path, sample_markdown_content):
    loader = DocumentLoader()
    file_path = tmp_path / "ep104_brian_chesky.md"
    file_path.write_text(sample_markdown_content, encoding="utf-8")
    doc = loader.load_file(file_path)

    extractor = MetadataExtractor()
    extractor.extract_metadata(doc)

    chunker = Chunker(chunk_size=200, chunk_overlap=30)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 0
    assert chunks[0].doc_id == doc.doc_id
    assert "section_header" in chunks[0].metadata


def test_transcript_pipeline_and_storage(tmp_path, sample_markdown_content):
    file_path = tmp_path / "ep104_brian_chesky.md"
    file_path.write_text(sample_markdown_content, encoding="utf-8")
    output_json = tmp_path / "output_chunks.json"

    pipeline = TranscriptIngestionPipeline()
    chunks = pipeline.process_file(file_path, output_json_path=output_json)

    assert len(chunks) > 0
    assert output_json.exists()

    with open(output_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == len(chunks)
    assert data[0]["doc_id"] == chunks[0].doc_id
