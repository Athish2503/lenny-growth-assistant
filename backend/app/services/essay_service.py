"""
EssayService for generating Ship30 style essays using prompt templates and LLM execution.
"""

import asyncio
from typing import Any, Dict, List, Optional
from app.services.llm_service import LLMService
from app.prompts.essay_prompt import build_essay_prompt


class EssayService:
    """
    EssayService implementing Ship30 essay generation:
    Input: message/topic, conversation history.
    Output: Ship30 formatted atomic essay.
    Uses prompt templates. No document retrieval. No artifacts.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service

    async def generate_essay(
        self,
        topic: str,
        history: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generates a Ship30 atomic essay given a prompt/topic and optional chat history.
        """
        # Step 1: Prompt Building using template
        prompt = build_essay_prompt(topic=topic, history=history)

        # Step 2: LLM Generation
        if self.llm_service:
            try:
                essay_text = await self.llm_service.generate(prompt)
            except Exception:
                essay_text = (
                    f"# How to Master {topic.strip()}\n\n"
                    f"Outlined essay topic: {topic.strip()}\n\n"
                    f"**Hook:** Most people struggle with {topic.lower()}, but it doesn't have to be hard.\n\n"
                    f"Here are 3 core principles for {topic}:\n\n"
                    f"1. **Start Small:** Focus on consistency over complexity.\n"
                    f"2. **Iterate Quickly:** Feedback loops accelerate growth.\n"
                    f"3. **Reflect Daily:** Track your progress to maintain momentum.\n\n"
                    f"**Takeaway:** Start applying this framework today."
                )
        else:
            # Default fallback format if LLMService is not provided
            essay_text = (
                f"# How to Master {topic.strip()}\n\n"
                f"Outlined essay topic: {topic.strip()}\n\n"
                f"**Hook:** Most people struggle with {topic.lower()}, but it doesn't have to be hard.\n\n"
                f"Here are 3 core principles for {topic}:\n\n"
                f"1. **Start Small:** Focus on consistency over complexity.\n"
                f"2. **Iterate Quickly:** Feedback loops accelerate growth.\n"
                f"3. **Reflect Daily:** Track your progress to maintain momentum.\n\n"
                f"**Takeaway:** Start applying this framework today."
            )

        return {
            "content": essay_text,
            "metadata": {
                "service": "EssayService",
                "essay_framework": "Ship30",
                "retrieval_performed": False,
                "has_artifacts": False,
                "is_essay": True,
            },
        }

    def process(self, message: str, history: Optional[List[Any]] = None) -> Dict[str, Any]:
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
            return loop.run_until_complete(self.generate_essay(message, history))
        else:
            return asyncio.run(self.generate_essay(message, history))
