"""
providers/__init__.py — Provider registry
"""

from .base import BaseProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider, GroqProvider, TogetherProvider

__all__ = [
    "BaseProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "GroqProvider",
    "TogetherProvider",
    "get_provider",
    "ALL_PROVIDERS",
    "get_all_models",
]

ALL_PROVIDERS: dict[str, type[BaseProvider]] = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    "together": TogetherProvider,
}


def get_provider(name: str, **kwargs) -> BaseProvider:
    cls = ALL_PROVIDERS.get(name, OllamaProvider)
    return cls(**kwargs)


def get_all_models() -> dict[str, list[str]]:
    return {
        name: cls.available_models
        for name, cls in ALL_PROVIDERS.items()
    }
