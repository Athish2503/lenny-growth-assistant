import pytest
from unittest.mock import AsyncMock

from app.prompts.essay_prompt import build_essay_prompt
from app.services.essay_service import EssayService


def test_build_essay_prompt():
    prompt = build_essay_prompt(
        topic="Product Strategy",
        history=[{"role": "user", "content": "How do I define product strategy?"}]
    )
    assert "Product Strategy" in prompt
    assert "User: How do I define product strategy?" in prompt
    assert "SHIP30 ESSAY WRITING RULES" in prompt
    assert "1250 words" in prompt


@pytest.mark.anyio
async def test_essay_service_generation_with_llm():
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = (
        "# Master Product Strategy\n\n"
        "**Hook:** Strategy isn't a long plan; it's a series of choices.\n\n"
        "1. **Focus:** Pick what NOT to do.\n"
        "2. **Leverage:** Double down on strength."
    )

    essay_service = EssayService(llm_service=mock_llm)
    result = await essay_service.generate_essay("Product Strategy")

    mock_llm.generate.assert_called_once()
    prompt_arg = mock_llm.generate.call_args[0][0]
    assert "Product Strategy" in prompt_arg

    assert "# Master Product Strategy" in result["content"]
    assert result["metadata"]["service"] == "EssayService"
    assert result["metadata"]["essay_framework"] == "Ship30"
    assert result["metadata"]["retrieval_performed"] is False
    assert result["metadata"]["has_artifacts"] is False
    assert result["metadata"]["is_essay"] is True


@pytest.mark.anyio
async def test_essay_service_fallback_without_llm():
    essay_service = EssayService(llm_service=None)
    result = await essay_service.generate_essay("Growth Loops")

    assert "# How to Master Growth Loops" in result["content"]
    assert result["metadata"]["service"] == "EssayService"
    assert result["metadata"]["retrieval_performed"] is False
    assert result["metadata"]["has_artifacts"] is False


def test_essay_service_sync_process():
    essay_service = EssayService(llm_service=None)
    result = essay_service.process("Growth Loops")

    assert "# How to Master Growth Loops" in result["content"]
    assert result["metadata"]["service"] == "EssayService"
