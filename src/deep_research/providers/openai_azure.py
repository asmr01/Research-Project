"""OpenAI / Azure OpenAI provider."""

from __future__ import annotations

import os
import logging

import httpx

from deep_research.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIAzureProvider(LLMProvider):
    name = "openai"

    def __init__(self) -> None:
        self.api_key = os.environ.get("GPT5_MINI_API_KEY", "")
        self.endpoint = os.environ.get(
            "GPT5_MINI_ENDPOINT",
            "https://api.openai.com/v1/chat/completions",
        )

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def call(
        self,
        prompt: str,
        model: str,
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> str:
        if not self.api_key:
            raise RuntimeError("GPT5_MINI_API_KEY not set")

        headers = {
            "Content-Type": "application/json",
        }

        # Detect Azure vs OpenAI endpoint
        if "openai.azure.com" in self.endpoint:
            headers["api-key"] = self.api_key
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                self.endpoint,
                headers=headers,
                json={
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
