"""
Prompt templates for Ship30 style essays.
"""

from typing import Any, List, Optional


SHIP30_ESSAY_PROMPT_TEMPLATE = """You are an expert essay writer skilled in the Ship 30 for 30 framework for high-impact atomic essays.

Your goal is to write a comprehensive, highly compelling, and deeply actionable Ship 30 for 30 style essay (approx. 1250 words) based on the user request and conversation history.

CONVERSATION HISTORY:
{history_str}

USER REQUEST:
{topic}

SHIP30 ESSAY WRITING RULES & FORMAT:
1. Title: Create a catchy, single-idea headline that promises a specific result or framework.
2. Strong Hook: Open with 1-2 punchy sentences (a bold claim, myth buster, or pattern interrupt) that hook the reader instantly.
3. Core Concept / Thesis: Introduce the central problem and why traditional approaches fail in a crisp introductory section.
4. Detailed Core Breakdown (Approx. 1250 Words):
   - Divide into 3-5 distinct sub-sections using bold markdown subheadings (###).
   - Use bold lead-ins for every bullet point or numbered item to ensure high skimmability.
   - Keep paragraphs short (1-3 sentences) with ample white space.
   - Provide concrete steps, real-world growth examples, frameworks, metrics, and actionable advice.
5. Clear Takeaway: End with a dedicated, memorable takeaway section summarizing the single golden rule or immediate call to action.

Generate the complete, fully-formatted Ship30 Atomic Essay now:"""


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
