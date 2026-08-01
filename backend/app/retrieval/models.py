from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class RetrievalResult:
    """
    Represents a single document/chunk retrieved by a retrieval algorithm.
    """
    doc_id: str
    chunk_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
