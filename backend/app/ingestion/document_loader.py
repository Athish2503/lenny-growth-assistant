import os
import re
from pathlib import Path
from typing import List, Union
from app.ingestion.models import Document


class DocumentLoader:
    """
    Loads and cleans transcript markdown files from disk.
    """

    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding

    def clean_markdown(self, raw_text: str) -> str:
        """
        Cleans raw markdown text:
        - Normalizes line endings to \n
        - Removes control characters and null bytes
        - Strips redundant trailing whitespace on lines
        - Reduces excessive consecutive blank lines (> 2) to 2
        """
        # Normalize line endings
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove null characters
        text = text.replace("\x00", "")
        
        # Strip trailing whitespace per line
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)
        
        # Collapse 3 or more consecutive newlines into 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text.strip()

    def load_file(self, file_path: Union[str, Path]) -> Document:
        """
        Loads a single markdown file, cleans it, and returns a Document object.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "r", encoding=self.encoding) as f:
            raw_content = f.read()

        cleaned_content = self.clean_markdown(raw_content)
        return Document(
            content=cleaned_content,
            source_path=str(path.resolve())
        )

    def load_directory(self, dir_path: Union[str, Path], recursive: bool = True) -> List[Document]:
        """
        Loads all markdown files (.md, .markdown) from a directory.
        """
        path = Path(dir_path)
        if not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")

        pattern = "**/*.md" if recursive else "*.md"
        files = list(path.glob(pattern))
        
        if recursive:
            files.extend(list(path.glob("**/*.markdown")))
        else:
            files.extend(list(path.glob("*.markdown")))

        documents = []
        for file in sorted(files):
            documents.append(self.load_file(file))

        return documents
