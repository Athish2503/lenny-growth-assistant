"""
Prompt builder for grounded Q&A tasks.
"""

from typing import Any, List, Optional
from app.retrieval.models import RetrievalResult


def build_qa_prompt(
    query: str,
    context_chunks: List[RetrievalResult],
    history: Optional[List[Any]] = None,
) -> str:
    """
    Builds a grounded prompt for the LLM using retrieved context chunks and conversation history.
    Ensures clear instructions to answer strictly based on provided facts and include citations.
    """
    formatted_context_items = []
    for idx, chunk in enumerate(context_chunks, start=1):
        doc_id = chunk.doc_id or "unknown"
        chunk_id = chunk.chunk_id or f"chunk-{idx}"
        title = chunk.metadata.get("title") or chunk.metadata.get("source") or doc_id

        context_block = (
            f"[Source {idx}]\n"
            f"ID: {chunk_id}\n"
            f"Title/Source: {title}\n"
            f"Content:\n{chunk.content}\n"
        )
        formatted_context_items.append(context_block)

    context_str = "\n".join(formatted_context_items) if formatted_context_items else "No relevant context found."

    formatted_history = []
    if history:
        for msg in history:
            role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else "user")
            content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else str(msg))
            formatted_history.append(f"{role.capitalize()}: {content}")

    history_str = "\n".join(formatted_history[-6:]) if formatted_history else ""
    history_block = f"CONVERSATION HISTORY:\n{history_str}\n\n" if history_str else ""

    prompt = f"""You are a helpful and precise growth assistant. Answer the user's question accurately using ONLY the provided context sources below.

INSTRUCTIONS:
1. Provide a concise, clear, and direct answer to the question.
2. Ground all claims in the provided context sources.
3. Cite sources inline or at the end of statements using source identifiers (e.g., [Source 1], [chunk_id], or source titles).
4. Ground all claims in the provided context sources without ungrounded speculation.
5. If the context does not contain enough information to answer the question, state that clearly.
6. Handle potential typos or misspelled names in the user's question (e.g., 'Ami Cora' -> 'Ami Vora') by providing answers for the correct entity while gently clarifying the correct name if appropriate.

{history_block}CONTEXT SOURCES:
{context_str}

QUESTION:
{query}

ANSWER:"""
    return prompt
