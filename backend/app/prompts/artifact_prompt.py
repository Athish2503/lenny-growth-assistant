"""
Prompt templates for Artifact generation (Markdown, HTML, CSS).
"""

from typing import Any, List, Optional


ARTIFACT_PROMPT_TEMPLATE = """You are an expert developer and technical author creating clean, structured, modular artifacts.

Generate a structured code artifact of type '{artifact_type}' based on the user request and conversation history.

CONVERSATION HISTORY:
{history_str}

USER REQUEST:
{prompt}

ARTIFACT TYPE: {artifact_type}

RULES:
1. If the request asks for an artifact based on the conversation history, synthesize all relevant insights, frameworks, key points, and summaries from the chat history into a complete, high-quality {artifact_type} document or component.
2. Provide valid, standard {artifact_type} content cleanly formatted.
3. For 'markdown': Use GitHub Flavored Markdown (GFM) with structured headers, bullet points, bold key terms, tables, and callout boxes.
4. For 'html': Use semantic HTML5 markup with clean embedded inline CSS/styling or modern flexbox/grid layout so it renders beautifully in an iframe.
5. For 'css': Provide modular CSS rulesets with custom CSS properties, flexbox/grid styles, and responsive classes.
6. Return the raw content directly without conversational preamble.

Generate the complete {artifact_type} artifact content now:"""


def build_artifact_prompt(
    prompt: str,
    artifact_type: str = "markdown",
    history: Optional[List[Any]] = None,
) -> str:
    """
    Formats the prompt template for generating structured artifacts (Markdown, HTML, CSS).
    """
    formatted_history = []
    if history:
        for msg in history:
            role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else "user")
            content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else str(msg))
            formatted_history.append(f"{role.capitalize()}: {content}")

    history_str = "\n".join(formatted_history) if formatted_history else "No previous conversation history."

    return ARTIFACT_PROMPT_TEMPLATE.format(
        prompt=prompt,
        artifact_type=artifact_type.lower(),
        history_str=history_str,
    )
