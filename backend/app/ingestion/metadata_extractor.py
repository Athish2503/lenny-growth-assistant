import re
from pathlib import Path
from typing import Dict, Any
import yaml
from app.ingestion.models import Document


class MetadataExtractor:
    """
    Extracts metadata (frontmatter, header titles, guest/host info, episode metadata)
    from markdown documents deterministically without calling LLMs.
    """

    def extract_metadata(self, document: Document) -> Dict[str, Any]:
        """
        Extracts metadata from document content and file path, updating and returning document metadata.
        """
        metadata: Dict[str, Any] = {
            "source_path": document.source_path,
            "filename": Path(document.source_path).name,
            "title": None,
            "guest": None,
            "episode_number": None,
            "date": None,
            "tags": [],
        }

        content = document.content

        # 1. Extract YAML Frontmatter if present
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if frontmatter_match:
            yaml_text = frontmatter_match.group(1)
            try:
                parsed_yaml = yaml.safe_load(yaml_text)
                if isinstance(parsed_yaml, dict):
                    metadata.update(parsed_yaml)
            except Exception:
                pass

        # 2. Infer Title from H1 (# Title)
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match and not metadata.get("title"):
            metadata["title"] = h1_match.group(1).strip()

        # Fallback title from filename
        if not metadata.get("title"):
            metadata["title"] = Path(document.source_path).stem.replace("-", " ").replace("_", " ").title()

        # 3. Extract guest / episode info from header patterns or filename
        # Pattern: Guest: <Name> or Episode <N>: <Name>
        guest_match = re.search(r"(?:Guest|Speaker):\s*([^\n]+)", content, re.IGNORECASE)
        if guest_match and not metadata.get("guest"):
            metadata["guest"] = guest_match.group(1).strip()

        ep_match = re.search(r"(?:Episode|Ep\.?)\s*#?(\d+)", content, re.IGNORECASE)
        if ep_match and not metadata.get("episode_number"):
            metadata["episode_number"] = int(ep_match.group(1))

        # Infer episode number or guest from filename if missing (e.g., ep104_brian_chesky.md)
        filename = metadata["filename"]
        if not metadata.get("episode_number"):
            fn_ep_match = re.search(r"(?:ep|episode)[_\-]?(\d+)", filename, re.IGNORECASE)
            if fn_ep_match:
                metadata["episode_number"] = int(fn_ep_match.group(1))

        document.metadata.update(metadata)
        return document.metadata
