"""Kimi provider (Moonshot AI)."""

from __future__ import annotations

import os
import logging

import httpx

from deep_research.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class KimiProvider(LLMProvider):
    name = "kimi"

    def __init__(self) -> None:
        self.api_key = os.environ.get("KIMI_API_KEY", "")
        self.endpoint = os.environ.get(
            "KIMI_ENDPOINT",
            "https://api.moonshot.cn/v1/chat/completions",
        )

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def call(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        if not self.api_key:
            raise RuntimeError("KIMI_API_KEY not set")

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
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
