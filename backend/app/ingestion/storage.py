import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Union
from app.ingestion.models import Chunk, Document


class Storage:
    """
    Saves document chunks to persistent storage (JSON or JSONL file) without generating embeddings or calling LLMs.
    """

    @staticmethod
    def save_chunks_to_json(chunks: List[Chunk], output_file: Union[str, Path]) -> str:
        """
        Saves a list of Chunk objects into a formatted JSON file.
        """
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        serialized = [asdict(chunk) for chunk in chunks]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

        return str(path.resolve())

    @staticmethod
    def save_chunks_to_jsonl(chunks: List[Chunk], output_file: Union[str, Path]) -> str:
        """
        Saves a list of Chunk objects into a JSON Lines (.jsonl) file.
        """
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")

        return str(path.resolve())
