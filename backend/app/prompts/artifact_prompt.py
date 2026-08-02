"""
Prompt templates for Artifact generation (Markdown, HTML, CSS).
"""

from typing import Any, List, Optional


ARTIFACT_PROMPT_TEMPLATE = """You are a Principal Frontend Architect and AI Product Engineer creating world-class, production-quality code artifacts.

Generate a structured artifact of type '{artifact_type}' based on the user request and conversation history.

CONVERSATION HISTORY:
{history_str}

USER REQUEST:
{prompt}

ARTIFACT TYPE: {artifact_type}

STRICT PRODUCTION RULES:
1. Unless the user explicitly requests Markdown (e.g. "markdown", "doc", "notes"), generate HTML + CSS.
2. For HTML artifacts:
   - Output self-contained HTML5 document with `<head>` and `<body>`.
   - Always include Tailwind CSS CDN script: `<script src="https://cdn.tailwindcss.com"></script>`
   - Include Google Fonts link for modern typography: Inter, Outfit, or Plus Jakarta Sans.
   - Use high-end design aesthetics: Linear/Raycast/Vercel inspiration, dark mode or sleek glassmorphism, soft glow accents, gradient buttons/borders, responsive grid layouts, card containers, micro-hover animations, clean spacing, and accessible color contrast.
   - If generating dashboards, landing pages, email templates, wireframes, roadmaps, UI components, resumes, or reports, make them fully styled, interactive, and visually stunning.
   - If charts are required, include Chart.js (`<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`) and initialize interactive canvas charts.
   - If diagrams are requested, include Mermaid.js (`<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>`) or clean SVG nodes.
3. For Markdown artifacts:
   - Provide GitHub Flavored Markdown (GFM) with rich headers, GFM tables, task lists (- [x]), callouts (> [!NOTE], > [!TIP], > [!IMPORTANT], > [!WARNING]), LaTeX math equations ($...$ or $$...$$), footnotes, and syntax-highlighted code blocks (including ```mermaid blocks).
4. Return ONLY raw executable content without conversational preamble, backtick markdown wrappers (e.g. do not wrap full HTML code in ```html ... ``` if type is html), or extra explanations. Return pure valid code.

Generate the complete {artifact_type} artifact content now:"""


def build_artifact_prompt(
    prompt: str,
    artifact_type: str = "html",
    history: Optional[List[Any]] = None,
) -> str:
    """
    Formats the prompt template for generating structured artifacts (HTML or Markdown).
    """
    formatted_history = []
    if history:
        for msg in history:
            role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else "user")
            content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else str(msg))
            formatted_history.append(f"{role.capitalize()}: {content}")

    history_str = "\n".join(formatted_history) if formatted_history else "No previous conversation history."

    # Determine default type: unless markdown is explicitly requested, default to html
    prompt_lower = prompt.lower()
    inferred_type = "markdown" if any(w in prompt_lower for w in ["markdown", "md file", "gfm", "raw text"]) else "html"
    res_type = artifact_type.lower() if artifact_type in ["html", "markdown", "css"] else inferred_type

    return ARTIFACT_PROMPT_TEMPLATE.format(
        prompt=prompt,
        artifact_type=res_type,
        history_str=history_str,
    )
