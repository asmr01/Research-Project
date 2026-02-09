"""Base provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers."""

    name: str = "base"

    @abstractmethod
    async def call(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to the LLM and return the response text."""
        ...

    def is_available(self) -> bool:
        """Check if required API keys / config are available."""
        return True
