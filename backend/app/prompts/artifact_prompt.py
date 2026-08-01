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
1. Provide valid, standard {artifact_type} content without conversational preamble or markdown codeblock wrappers if raw output is required, or well-structured clean code.
2. For 'markdown': Use clean GFM syntax with headers, lists, bold text, and tables where applicable.
3. For 'html': Use clean semantic HTML5 markup (e.g. standard tags, accessible elements). Do NOT include external script dependencies unless requested.
4. For 'css': Provide clean CSS rulesets with modern layout techniques (Flexbox/Grid), custom variables, and responsive design properties.
5. Do NOT attempt to render the frontend output. Return only the structured artifact definition and code content.

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
