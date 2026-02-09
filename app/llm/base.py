# app/llm/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMClient(ABC):
    """
    Abstract base class for any LLM provider.
    This allows us to switch providers without touching business logic.
    """

    @abstractmethod
    async def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Takes sanitized user text and returns structured intent JSON.
        """
        pass
