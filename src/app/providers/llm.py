from typing import Any

from pydantic import BaseModel

from app.core.config import get_settings


class LLMProviderError(Exception):
    pass


class LLMProvider:
    def __init__(
        self, provider: str = "openrouter", model: str | None = None, api_key: str | None = None
    ):
        settings = get_settings()
        self.provider = provider
        self.model = model or getattr(settings, "llm_model", None) or "gpt-4o-mini"
        self.api_key = api_key or getattr(settings, "llm_api_key", None)
        self.base_url = getattr(settings, "llm_base_url", None) or "https://api.openrouter.ai/v1"
        self.timeout = getattr(settings, "llm_timeout_seconds", 60)
        self.max_tokens = getattr(settings, "llm_max_tokens", 4096)

    async def complete(
        self, messages: list[dict[str, str]], response_schema: type[BaseModel] | None = None
    ) -> dict[str, Any]:
        if not self.api_key:
            raise LLMProviderError("LLM credentials not configured")
        # Provider boundary ready - actual call not executed without credentials in this phase
        raise LLMProviderError("LLM provider not fully configured for this environment")


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    return LLMProvider(
        provider=getattr(settings, "llm_provider", "openrouter"),
        model=getattr(settings, "llm_model", None),
        api_key=getattr(settings, "llm_api_key", None),
    )


__all__ = ["LLMProvider", "LLMProviderError", "get_llm_provider"]
