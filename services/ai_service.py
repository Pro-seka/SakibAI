"""
services/ai_service.py — Central AI orchestration service
"""

from typing import Iterator
import streamlit as st
from database.db import get_setting
from providers import get_provider, OllamaProvider


def get_active_provider():
    """Build the active provider from settings."""
    provider_name = get_setting("provider", "ollama")
    kwargs = {}
    if provider_name == "openai":
        kwargs["api_key"] = get_setting("openai_api_key", "")
    elif provider_name == "groq":
        kwargs["api_key"] = get_setting("groq_api_key", "")
    elif provider_name == "together":
        kwargs["api_key"] = get_setting("together_api_key", "")
    return get_provider(provider_name, **kwargs)


def stream_response(
    messages: list[dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    system_prompt: str = "",
) -> Iterator[str]:
    """
    Stream AI response tokens.
    messages: list of {role, content} dicts (raw history, no system msg)
    """
    provider = get_active_provider()

    full_messages = provider.build_prompt_messages(messages, system_prompt)

    yield from provider.chat(
        messages=full_messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )


def single_response(
    prompt: str,
    system_prompt: str = "",
    model: str = "",
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Get a single non-streaming response — used by study tools, PDF chat, etc."""
    provider = get_active_provider()
    if not model:
        model = get_setting("default_model", "llama3")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    full_response = ""
    for token in provider.chat(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    ):
        full_response += token
    return full_response.strip()


def generate_title(first_message: str) -> str:
    """Generate a short conversation title from the first user message."""
    prompt = (
        f"Generate a very short title (3-6 words) for a chat that starts with:\n"
        f'"{first_message[:200]}"\n\n'
        f"Reply with ONLY the title, no quotes, no punctuation at the end."
    )
    title = single_response(prompt, temperature=0.3, max_tokens=20)
    return title[:60] if title else "New Chat"
