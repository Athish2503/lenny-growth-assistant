import pytest
from unittest.mock import AsyncMock

from app.prompts.artifact_prompt import build_artifact_prompt
from app.services.artifact_service import ArtifactService


def test_build_artifact_prompt():
    prompt = build_artifact_prompt(
        prompt="Create landing page header",
        artifact_type="html",
        history=[{"role": "user", "content": "Need HTML code"}]
    )
    assert "Create landing page header" in prompt
    assert "ARTIFACT TYPE: html" in prompt
    assert "User: Need HTML code" in prompt
    assert "Do NOT attempt to render the frontend output" in prompt


@pytest.mark.anyio
async def test_artifact_service_markdown_with_llm():
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "# Component Spec\n\n- Feature 1\n- Feature 2"

    service = ArtifactService(llm_service=mock_llm)
    result = await service.generate_artifact(
        prompt="Write markdown spec",
        artifact_type="markdown",
        title="Spec Doc"
    )

    mock_llm.generate.assert_called_once()
    assert result["title"] == "Spec Doc"
    assert result["artifact_type"] == "markdown"
    assert result["content"] == "# Component Spec\n\n- Feature 1\n- Feature 2"
    assert result["version"] == 1
    assert result["metadata"]["service"] == "ArtifactService"
    assert result["metadata"]["frontend_rendered"] is False


@pytest.mark.anyio
async def test_artifact_service_html_generation():
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "<div class='card'><h2>Title</h2></div>"

    service = ArtifactService(llm_service=mock_llm)
    result = await service.generate_artifact(
        prompt="HTML Card Component",
        artifact_type="html"
    )

    assert result["artifact_type"] == "html"
    assert result["content"] == "<div class='card'><h2>Title</h2></div>"
    assert result["metadata"]["frontend_rendered"] is False


@pytest.mark.anyio
async def test_artifact_service_css_generation():
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = ".card { padding: 1rem; border: 1px solid #ccc; }"

    service = ArtifactService(llm_service=mock_llm)
    result = await service.generate_artifact(
        prompt="CSS Card Style",
        artifact_type="css"
    )

    assert result["artifact_type"] == "css"
    assert result["content"] == ".card { padding: 1rem; border: 1px solid #ccc; }"
    assert result["metadata"]["frontend_rendered"] is False


@pytest.mark.anyio
async def test_artifact_service_fallback_without_llm():
    service = ArtifactService(llm_service=None)

    md_result = await service.generate_artifact("Create overview", artifact_type="markdown")
    assert md_result["artifact_type"] == "markdown"
    assert "Overview" in md_result["content"]

    html_result = await service.generate_artifact("Create html button", artifact_type="html")
    assert html_result["artifact_type"] == "html"
    assert "<section class=\"artifact-container\">" in html_result["content"]

    css_result = await service.generate_artifact("Create css styles", artifact_type="css")
    assert css_result["artifact_type"] == "css"
    assert ":root {" in css_result["content"]


def test_artifact_service_sync_process():
    service = ArtifactService(llm_service=None)
    result = service.process("Create card html", artifact_type="html", title="Card HTML")

    assert result["title"] == "Card HTML"
    assert result["artifact_type"] == "html"
    assert result["metadata"]["service"] == "ArtifactService"
