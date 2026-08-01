from pathlib import Path
from typing import List, Union, Optional
from app.ingestion.models import Document, Chunk
from app.ingestion.document_loader import DocumentLoader
from app.ingestion.metadata_extractor import MetadataExtractor
from app.ingestion.chunker import Chunker
from app.ingestion.storage import Storage


class TranscriptIngestionPipeline:
    """
    Pipeline orchestrating transcript loading, cleaning, metadata extraction, chunking, and storage.
    """

    def __init__(
        self,
        loader: Optional[DocumentLoader] = None,
        extractor: Optional[MetadataExtractor] = None,
        chunker: Optional[Chunker] = None,
        storage: Optional[Storage] = None,
    ):
        self.loader = loader or DocumentLoader()
        self.extractor = extractor or MetadataExtractor()
        self.chunker = chunker or Chunker()
        self.storage = storage or Storage()

    def process_file(self, file_path: Union[str, Path], output_json_path: Optional[Union[str, Path]] = None) -> List[Chunk]:
        """
        Processes a single transcript markdown file into saved chunks.
        """
        doc = self.loader.load_file(file_path)
        self.extractor.extract_metadata(doc)
        chunks = self.chunker.chunk_document(doc)

        if output_json_path:
            self.storage.save_chunks_to_json(chunks, output_json_path)

        return chunks

    def process_directory(self, dir_path: Union[str, Path], output_json_path: Optional[Union[str, Path]] = None) -> List[Chunk]:
        """
        Processes a directory of transcript markdown files into saved chunks.
        """
        docs = self.loader.load_directory(dir_path)
        all_chunks: List[Chunk] = []

        for doc in docs:
            self.extractor.extract_metadata(doc)
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)

        if output_json_path:
            self.storage.save_chunks_to_json(all_chunks, output_json_path)

        return all_chunks


__all__ = [
    "Document",
    "Chunk",
    "DocumentLoader",
    "MetadataExtractor",
    "Chunker",
    "Storage",
    "TranscriptIngestionPipeline",
]
