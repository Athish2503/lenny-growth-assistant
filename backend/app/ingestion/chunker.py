import re
import uuid
from typing import List, Optional, Dict, Any
from app.ingestion.models import Document, Chunk


class Chunker:
    """
    Header-Aware & Recursive Character Chunker for markdown transcript files.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def _split_text_recursively(self, text: str, separators: List[str]) -> List[str]:
        """
        Splits text recursively using the first matching separator to keep chunks <= chunk_size.
        """
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            # Fallback hard-cut if no separators remain
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

        separator = separators[0]
        new_separators = separators[1:]

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        final_chunks = []
        current_chunk = []
        current_len = 0

        for split in splits:
            split_len = len(split) + (len(separator) if separator else 0)
            
            # If a single split item is larger than chunk_size, split it further
            if len(split) > self.chunk_size:
                if current_chunk:
                    joined = (separator or "").join(current_chunk)
                    final_chunks.append(joined)
                    current_chunk = []
                    current_len = 0
                sub_chunks = self._split_text_recursively(split, new_separators)
                final_chunks.extend(sub_chunks)
                continue

            if current_len + split_len > self.chunk_size:
                joined = (separator or "").join(current_chunk)
                final_chunks.append(joined)
                
                # Apply overlap logic
                overlap_chars = 0
                overlap_chunk = []
                for item in reversed(current_chunk):
                    if overlap_chars + len(item) <= self.chunk_overlap:
                        overlap_chunk.insert(0, item)
                        overlap_chars += len(item)
                    else:
                        break
                current_chunk = overlap_chunk
                current_len = sum(len(x) for x in current_chunk)

            current_chunk.append(split)
            current_len += split_len

        if current_chunk:
            joined = (separator or "").join(current_chunk)
            final_chunks.append(joined)

        return [c.strip() for c in final_chunks if c.strip()]

    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Chunks a Document by headers first, then recursively by characters/paragraphs.
        """
        # Split by Markdown Headers (#, ##, ###, ####)
        header_pattern = r"(?m)^(#{1,4}\s+.*$)"
        parts = re.split(header_pattern, document.content)

        sections: List[Dict[str, str]] = []
        current_header = "Preamble"
        current_text = ""

        for part in parts:
            if re.match(r"^#{1,4}\s+", part):
                if current_text.strip():
                    sections.append({"header": current_header, "text": current_text.strip()})
                current_header = part.strip("#").strip()
                current_text = part + "\n"
            else:
                current_text += part

        if current_text.strip():
            sections.append({"header": current_header, "text": current_text.strip()})

        raw_chunks: List[Dict[str, Any]] = []
        for section in sections:
            header_title = section["header"]
            sec_text = section["text"]

            if len(sec_text) <= self.chunk_size:
                raw_chunks.append({"header": header_title, "text": sec_text})
            else:
                sub_splits = self._split_text_recursively(sec_text, self.separators)
                for split in sub_splits:
                    raw_chunks.append({"header": header_title, "text": split})

        # Build Chunk objects with metadata lineage
        chunks: List[Chunk] = []
        search_offset = 0

        for idx, item in enumerate(raw_chunks):
            content_str = item["text"]
            start_pos = document.content.find(content_str, search_offset)
            if start_pos != -1:
                end_pos = start_pos + len(content_str)
                search_offset = max(search_offset, start_pos + 1)
            else:
                start_pos, end_pos = None, None

            chunk_meta = dict(document.metadata)
            chunk_meta["section_header"] = item["header"]

            chunk = Chunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=document.doc_id,
                content=content_str,
                chunk_index=idx,
                metadata=chunk_meta,
                start_char=start_pos,
                end_char=end_pos
            )
            chunks.append(chunk)

        return chunks
