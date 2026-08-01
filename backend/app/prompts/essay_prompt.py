"""
Prompt templates for Ship30 style essays.
"""

from typing import Any, List, Optional


SHIP30_ESSAY_PROMPT_TEMPLATE = """You are an expert essay writer skilled in the Ship30 (Ship 30 for 30) framework for atomic essays.

Your goal is to write a compelling, clear, and actionable atomic essay based on the user's input request and conversation history.

CONVERSATION HISTORY:
{history_str}

USER REQUEST:
{topic}

SHIP30 ESSAY WRITING RULES:
1. Title: Catchy, clear, single-idea headline that promises a specific outcome or insight.
2. Hook: 1-2 punchy lines that open the essay and hook the reader's attention instantly.
3. Core Concept / Thesis: Introduce the main idea clearly without fluff.
4. Main Points / Sub-headings: Break down the core idea into 3-5 distinct, actionable takeaways using clear bullet points or numbered lists.
5. Conclusion / Takeaway: Reiterate the core message with a strong summary statement or call to action.
6. Keep it concise, punchy, formatted cleanly with markdown headers, bold text, and white space for maximum readability.
7. Do NOT perform web searches or document retrieval.
8. Do NOT create external artifacts or files.

Generate the complete Ship30 Atomic Essay now:"""


def build_essay_prompt(topic: str, history: Optional[List[Any]] = None) -> str:
    """
    Formats the prompt template for generating a Ship30 atomic essay.
    """
    formatted_history = []
    if history:
        for msg in history:
            role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else "user")
            content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else str(msg))
            formatted_history.append(f"{role.capitalize()}: {content}")
    
    history_str = "\n".join(formatted_history) if formatted_history else "No previous conversation history."
    
    return SHIP30_ESSAY_PROMPT_TEMPLATE.format(
        topic=topic,
        history_str=history_str,
    )
