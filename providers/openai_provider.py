"""
providers/openai_provider.py — OpenAI-compatible API provider
Works with: OpenAI, Groq, Together AI, LM Studio, Anyscale, Perplexity, etc.
"""

import os
from typing import Iterator
from .base import BaseProvider

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]

GROQ_MODELS = [
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "gemma2-9b-it",
]

TOGETHER_MODELS = [
    "meta-llama/Llama-3-70b-chat-hf",
    "meta-llama/Llama-3-8b-chat-hf",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "Qwen/Qwen2-72B-Instruct",
]


class OpenAIProvider(BaseProvider):
    name = "openai"
    display_name = "OpenAI"
    available_models = OPENAI_MODELS

    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or "https://api.openai.com/v1"

    def _client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
        return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key)

    def chat(
        self,
        messages: list[dict],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True,
    ) -> Iterator[str]:
        if not self.is_available():
            yield "⚠️ OpenAI API key not configured. Go to Settings to add it."
            return
        try:
            client = self._client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
            if stream:
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
            else:
                yield response.choices[0].message.content or ""
        except Exception as e:
            yield f"\n\n⚠️ **OpenAI Error:** {e}"


class GroqProvider(BaseProvider):
    name = "groq"
    display_name = "Groq (Ultra-Fast)"
    available_models = GROQ_MODELS

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")

    def _client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package required for Groq. Run: pip install openai")
        return OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")

    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key)

    def chat(
        self,
        messages: list[dict],
        model: str = "llama3-70b-8192",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True,
    ) -> Iterator[str]:
        if not self.is_available():
            yield "⚠️ Groq API key not configured. Go to Settings to add it."
            return
        try:
            client = self._client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
            if stream:
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
            else:
                yield response.choices[0].message.content or ""
        except Exception as e:
            yield f"\n\n⚠️ **Groq Error:** {e}"


class TogetherProvider(BaseProvider):
    name = "together"
    display_name = "Together AI"
    available_models = TOGETHER_MODELS

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY", "")

    def _client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package required. Run: pip install openai")
        return OpenAI(api_key=self.api_key, base_url="https://api.together.xyz/v1")

    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key)

    def chat(
        self,
        messages: list[dict],
        model: str = "meta-llama/Llama-3-8b-chat-hf",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True,
    ) -> Iterator[str]:
        if not self.is_available():
            yield "⚠️ Together AI API key not configured. Go to Settings to add it."
            return
        try:
            client = self._client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
            if stream:
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
            else:
                yield response.choices[0].message.content or ""
        except Exception as e:
            yield f"\n\n⚠️ **Together AI Error:** {e}"
