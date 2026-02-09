"""LLM providers - unified interface for multiple AI models."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Provider registry
_PROVIDERS: dict[str, Any] = {}


def _ensure_providers_loaded() -> None:
    """Lazy-load providers on first use."""
    if _PROVIDERS:
        return

    from deep_research.providers.claude import ClaudeProvider
    from deep_research.providers.gemini import GeminiProvider
    from deep_research.providers.openai_azure import OpenAIAzureProvider
    from deep_research.providers.openrouter import OpenRouterProvider
    from deep_research.providers.kimi import KimiProvider

    _PROVIDERS["claude"] = ClaudeProvider()
    _PROVIDERS["gemini"] = GeminiProvider()
    _PROVIDERS["openai"] = OpenAIAzureProvider()
    _PROVIDERS["azure"] = OpenAIAzureProvider()
    _PROVIDERS["openrouter"] = OpenRouterProvider()
    _PROVIDERS["kimi"] = KimiProvider()


# Model aliases → (provider, model_id)
MODEL_ALIASES: dict[str, tuple[str, str]] = {
    "opus": ("claude", "claude-opus-4-20250514"),
    "sonnet": ("claude", "claude-sonnet-4-20250514"),
    "haiku": ("claude", "claude-haiku-4-5-20251001"),
    "flash": ("gemini", "gemini-2.0-flash"),
    "pro": ("gemini", "gemini-2.5-pro-preview-06-05"),
    "gpt5-mini": ("openai", "gpt-5-mini"),
    "grok": ("openrouter", "x-ai/grok-3"),
    "grok-3": ("openrouter", "x-ai/grok-3"),
    "grok-4": ("openrouter", "x-ai/grok-4"),
    "kimi": ("kimi", "kimi-k2-0711"),
}


def parse_model(model_str: str) -> tuple[str, str]:
    """Parse 'provider:model' or alias into (provider, model_id).

    Examples:
        'haiku' → ('claude', 'claude-haiku-4-5-20251001')
        'gemini:flash' → ('gemini', 'gemini-2.0-flash')
        'claude:opus' → ('claude', 'claude-opus-4-20250514')
    """
    if ":" in model_str:
        provider, model = model_str.split(":", 1)
        # Check if model part is an alias
        if model in MODEL_ALIASES:
            _, model_id = MODEL_ALIASES[model]
            return provider, model_id
        return provider, model

    if model_str in MODEL_ALIASES:
        return MODEL_ALIASES[model_str]

    # Default to claude provider
    return "claude", model_str


async def call_llm(prompt: str, model: str = "haiku", temperature: float = 0.7) -> str:
    """Call an LLM with the given prompt.

    Args:
        prompt: The prompt to send.
        model: Model string (alias or 'provider:model').
        temperature: Sampling temperature.

    Returns:
        The model's response text.
    """
    _ensure_providers_loaded()

    provider_name, model_id = parse_model(model)
    provider = _PROVIDERS.get(provider_name)

    if not provider:
        raise ValueError(f"Unknown provider: {provider_name}")

    logger.debug(f"Calling {provider_name}:{model_id}")
    return await provider.call(prompt, model_id, temperature=temperature)
