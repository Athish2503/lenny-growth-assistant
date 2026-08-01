"""
ArtifactService for generating structured artifacts (Markdown, HTML, CSS).
Returns structured artifact definitions without frontend rendering.
"""

import asyncio
from typing import Any, Dict, List, Optional
from app.services.llm_service import LLMService
from app.prompts.artifact_prompt import build_artifact_prompt


class ArtifactService:
    """
    ArtifactService for structured artifact generation:
    Input: prompt/request, artifact_type (markdown, html, css), title, conversation history.
    Output: Structured artifact payload containing content, metadata, title, and type.
    No frontend rendering.
    """

    SUPPORTED_TYPES = {"markdown", "html", "css"}

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service

    def _infer_artifact_type(self, prompt: str, artifact_type: str = "markdown") -> str:
        artifact_type_lower = artifact_type.lower()
        if artifact_type_lower in self.SUPPORTED_TYPES:
            return artifact_type_lower

        prompt_lower = prompt.lower()
        if "html" in prompt_lower:
            return "html"
        elif "css" in prompt_lower or "stylesheet" in prompt_lower or "style" in prompt_lower:
            return "css"
        return "markdown"

    def _get_fallback_content(self, prompt: str, artifact_type: str, title: str) -> str:
        if artifact_type == "html":
            return (
                f"<!-- {title} -->\n"
                f"<section class=\"artifact-container\">\n"
                f"  <header>\n"
                f"    <h1>{title}</h1>\n"
                f"  </header>\n"
                f"  <main>\n"
                f"    <p>Generated HTML component for: {prompt}</p>\n"
                f"  </main>\n"
                f"</section>"
            )
        elif artifact_type == "css":
            return (
                f"/* {title} */\n"
                f":root {{\n"
                f"  --primary-color: #2563eb;\n"
                f"  --bg-color: #f8fafc;\n"
                f"  --text-color: #0f172a;\n"
                f"}}\n\n"
                f".artifact-container {{\n"
                f"  background-color: var(--bg-color);\n"
                f"  color: var(--text-color);\n"
                f"  padding: 1.5rem;\n"
                f"  border-radius: 0.5rem;\n"
                f"}}"
            )
        else: # markdown
            return (
                f"# {title}\n\n"
                f"## Overview\n"
                f"Generated markdown document for prompt: `{prompt}`.\n\n"
                f"## Key Details\n"
                f"- **Artifact Type:** Markdown\n"
                f"- **Render Required:** False (Structured data only)\n"
            )

    async def generate_artifact(
        self,
        prompt: str,
        artifact_type: str = "markdown",
        title: Optional[str] = None,
        history: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generates a structured artifact (Markdown, HTML, or CSS) dictionary without rendering.
        """
        resolved_type = self._infer_artifact_type(prompt, artifact_type)
        artifact_title = title or f"Generated {resolved_type.upper()} Artifact"

        formatted_prompt = build_artifact_prompt(
            prompt=prompt,
            artifact_type=resolved_type,
            history=history,
        )

        if self.llm_service:
            content = await self.llm_service.generate(formatted_prompt)
        else:
            content = self._get_fallback_content(prompt, resolved_type, artifact_title)

        return {
            "title": artifact_title,
            "artifact_type": resolved_type,
            "content": content,
            "version": 1,
            "metadata": {
                "service": "ArtifactService",
                "artifact_type": resolved_type,
                "frontend_rendered": False,
                "retrieval_performed": False,
                "has_artifacts": True,
            },
        }

    def process(
        self,
        message: str,
        history: Optional[List[Any]] = None,
        artifact_type: str = "markdown",
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous interface wrapper for compatibility with chat orchestrators.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(
                self.generate_artifact(
                    prompt=message,
                    artifact_type=artifact_type,
                    title=title,
                    history=history,
                )
            )
        else:
            return asyncio.run(
                self.generate_artifact(
                    prompt=message,
                    artifact_type=artifact_type,
                    title=title,
                    history=history,
                )
            )
