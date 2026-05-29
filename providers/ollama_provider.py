"""
providers/ollama_provider.py — Local Ollama inference
"""

import json
import requests
from typing import Iterator
from .base import BaseProvider

OLLAMA_BASE = "http://localhost:11434"

OLLAMA_MODELS = [
    "llama3",
    "llama3:8b",
    "llama3:70b",
    "llama3.1",
    "mistral",
    "mistral:7b",
    "gemma",
    "gemma:7b",
    "gemma2",
    "qwen",
    "qwen2",
    "codellama",
    "phi3",
    "phi3:mini",
    "deepseek-coder",
    "vicuna",
    "neural-chat",
]


class OllamaProvider(BaseProvider):
    name = "ollama"
    display_name = "Ollama (Local)"
    available_models = OLLAMA_MODELS

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def get_local_models(self) -> list[str]:
        try:
            r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
            if r.status_code == 200:
                data = r.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def chat(
        self,
        messages: list[dict],
        model: str = "llama3",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True,
    ) -> Iterator[str]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        try:
            with requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json=payload,
                stream=True,
                timeout=120,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.ConnectionError:
            yield "\n\n⚠️ **Ollama not running.** Start it with `ollama serve` in a terminal."
        except Exception as e:
            yield f"\n\n⚠️ **Error:** {e}"
