"""
providers/base.py — Abstract base for all AI providers
"""

from abc import ABC, abstractmethod
from typing import Iterator


class BaseProvider(ABC):
    """All AI providers must implement this interface."""

    name: str = "base"
    display_name: str = "Base Provider"
    available_models: list[str] = []

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True,
    ) -> Iterator[str]:
        """Yield response tokens one at a time."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if provider is reachable."""
        ...

    def build_prompt_messages(self, history: list[dict], system_prompt: str) -> list[dict]:
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        for m in history:
            msgs.append({"role": m["role"], "content": m["content"]})
        return msgs
