"""
Gemini AI Provider - Clean API integration
"""

from typing import List, Dict, Generator
import google.generativeai as genai
from config.settings import DEFAULT_MODEL_NAME
from utils.logger import setup_logging

logger = setup_logging()

class GeminiProvider:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=DEFAULT_MODEL_NAME,
            system_instruction="You are SakibAI, a professional, helpful AI assistant."
        )
        logger.info("Gemini provider initialized")
    
    def _filter_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, any]]:
        filtered = []
        for msg in messages:
            role = msg.get("role", "").lower()
            content = msg.get("content", "")
            if role not in ["user", "assistant"]:
                continue
            if not content or not content.strip():
                continue
            gemini_role = "model" if role == "assistant" else "user"
            filtered.append({"role": gemini_role, "parts": [content]})
        return filtered
    
    def stream_chat(self, message: str, history: List[Dict[str, str]],
                    temperature: float = 0.7, max_tokens: int = 2000) -> Generator[str, None, None]:
        try:
            filtered_history = self._filter_messages(history)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": 0.95,
                "top_k": 40
            }
            chat = self.model.start_chat(history=filtered_history)
            response = chat.send_message(message, generation_config=generation_config, stream=True)
            for chunk in response:
                if chunk.text and chunk.text.strip():
                    yield chunk.text
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"❌ Error: {str(e)}"