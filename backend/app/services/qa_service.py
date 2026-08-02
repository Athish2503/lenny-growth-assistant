"""
QAService for handling question answering via Hybrid Retrieval, Prompt Building, and LLM generation.
"""

from typing import Any, Dict, List, Optional
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.models import RetrievalResult
from app.retrieval.query_contextualizer import contextualize_query
from app.services.llm_service import LLMService
from app.prompts.qa_prompt import build_qa_prompt


class QAService:
    """
    QAService implementing the workflow:
    Question -> Contextualized Query -> Hybrid Retrieval -> Prompt Builder -> LLM -> Grounded Answer with citations.
    No essay generation. No artifacts.
    """

    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        llm_service: Optional[LLMService] = None,
        top_k: int = 5,
    ):
        self.retriever = retriever or HybridRetriever()
        self.llm_service = llm_service
        self.top_k = top_k

    async def answer_question(
        self,
        query: str,
        history: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the Q&A workflow for a user question.
        Returns a dictionary containing content, citations/sources, and metadata.
        """
        # Contextualize query with conversation history for anaphora resolution
        search_query = contextualize_query(query, history)

        # Step 1 & 2: Hybrid Retrieval
        retrieved_chunks: List[RetrievalResult] = await self.retriever.retrieve(
            query=search_query,
            top_k=self.top_k,
        )

        # Step 3: Prompt Building with conversation history
        prompt = build_qa_prompt(query=query, context_chunks=retrieved_chunks, history=history)

        # Step 4 & 5: LLM Generation / Grounded Answer
        if self.llm_service:
            try:
                answer_text = await self.llm_service.generate(prompt)
            except Exception:
                sources_summary = ", ".join(
                    f"[{c.chunk_id}]" for c in retrieved_chunks
                ) if retrieved_chunks else "No sources"
                answer_text = (
                    f"Based on retrieved sources ({sources_summary}):\n"
                    f"Answer to query '{query}' grounded in retrieved context."
                )
        else:
            # Fallback/default structured answer format if LLMService is not passed
            sources_summary = ", ".join(
                f"[{c.chunk_id}]" for c in retrieved_chunks
            ) if retrieved_chunks else "No sources"
            answer_text = (
                f"Based on retrieved sources ({sources_summary}):\n"
                f"Answer to query '{query}' grounded in retrieved context."
            )

        # Build citations structure
        citations = [
            {
                "doc_id": chunk.doc_id,
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "score": chunk.score,
                "metadata": chunk.metadata,
            }
            for chunk in retrieved_chunks
        ]

        return {
            "content": answer_text,
            "citations": citations,
            "metadata": {
                "service": "QAService",
                "retrieved_count": len(retrieved_chunks),
                "has_artifacts": False,
                "is_essay": False,
            },
        }

    def process(self, message: str, history: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Synchronous interface wrapper for compatibility with chat orchestrator.
        """
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If called inside an active event loop, execute via task or async caller
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(self.answer_question(message, history))
        else:
            return asyncio.run(self.answer_question(message, history))
