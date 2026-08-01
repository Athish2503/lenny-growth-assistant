import pytest
from unittest.mock import AsyncMock, MagicMock

from app.retrieval.models import RetrievalResult
from app.services.qa_service import QAService
from app.prompts.qa_prompt import build_qa_prompt


def test_qa_prompt_builder():
    chunks = [
        RetrievalResult(
            doc_id="doc1",
            chunk_id="c1",
            content="Product-led growth focuses on self-serve onboarding.",
            score=0.9,
            metadata={"title": "PLG Guide"},
        )
    ]
    prompt = build_qa_prompt("What is PLG?", chunks)
    assert "Product-led growth focuses on self-serve onboarding." in prompt
    assert "[Source 1]" in prompt
    assert "PLG Guide" in prompt
    assert "What is PLG?" in prompt


@pytest.mark.anyio
async def test_qa_service_workflow():
    # Mock retriever
    mock_retriever = AsyncMock()
    mock_chunks = [
        RetrievalResult(
            doc_id="doc_123",
            chunk_id="chunk_1",
            content="Retention rate measures how many users continue using a product.",
            score=0.95,
            metadata={"source": "lenny_transcript_1.md"},
        )
    ]
    mock_retriever.retrieve.return_value = mock_chunks

    # Mock LLM service
    mock_llm_service = AsyncMock()
    mock_llm_service.generate.return_value = (
        "Retention rate measures active users over time [Source 1]."
    )

    qa_service = QAService(
        retriever=mock_retriever,
        llm_service=mock_llm_service,
        top_k=3,
    )

    result = await qa_service.answer_question("How is retention rate measured?")

    # Verify retrieval call
    mock_retriever.retrieve.assert_called_once_with(
        query="How is retention rate measured?",
        top_k=3,
    )

    # Verify LLM call
    mock_llm_service.generate.assert_called_once()
    prompt_arg = mock_llm_service.generate.call_args[0][0]
    assert "Retention rate measures how many users continue using a product." in prompt_arg

    # Verify output structure
    assert result["content"] == "Retention rate measures active users over time [Source 1]."
    assert len(result["citations"]) == 1
    assert result["citations"][0]["chunk_id"] == "chunk_1"
    assert result["citations"][0]["doc_id"] == "doc_123"
    assert result["metadata"]["has_artifacts"] is False
    assert result["metadata"]["is_essay"] is False


@pytest.mark.anyio
async def test_qa_service_fallback_without_llm():

    mock_retriever = AsyncMock()
    mock_retriever.retrieve.return_value = [
        RetrievalResult(
            doc_id="doc_1",
            chunk_id="chunk_10",
            content="Viral loop generates network effects.",
            score=0.88,
            metadata={},
        )
    ]

    qa_service = QAService(retriever=mock_retriever, llm_service=None)
    result = await qa_service.answer_question("What is a viral loop?")

    assert "grounded in retrieved context" in result["content"]
    assert len(result["citations"]) == 1
    assert result["citations"][0]["chunk_id"] == "chunk_10"
