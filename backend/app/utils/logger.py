import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("lenny_growth_assistant")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_request_metrics(
    request_id: str,
    session_id: str,
    model: str,
    retrieval_latency_ms: float,
    llm_latency_ms: float,
    total_response_time_ms: float,
    retrieved_doc_count: int,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Structured logging utility to record request metrics.
    """
    log_payload = {
        "event": "chat_request_completed",
        "request_id": request_id,
        "session_id": session_id,
        "model": model,
        "retrieval_latency_ms": round(retrieval_latency_ms, 2),
        "llm_latency_ms": round(llm_latency_ms, 2),
        "total_response_time_ms": round(total_response_time_ms, 2),
        "retrieved_doc_count": retrieved_doc_count,
    }
    if extra:
        log_payload.update(extra)
    logger.info(json.dumps(log_payload))
