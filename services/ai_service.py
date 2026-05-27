"""
AI Service Layer - Handles all AI interactions
"""

import streamlit as st
from typing import List, Dict, Generator
from config.settings import GEMINI_API_KEY
from providers.gemini import GeminiProvider
from utils.logger import setup_logging

logger = setup_logging()

class AIService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        self.provider = GeminiProvider(api_key=GEMINI_API_KEY)
        logger.info("AI Service initialized")
    
    def stream_message(self, message: str, conversation_history: List[Dict[str, str]],
                       temperature: float = 0.7, max_tokens: int = 2000) -> Generator[str, None, None]:
        try:
            for chunk in self.provider.stream_chat(
                message=message,
                history=conversation_history,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                if chunk:
                    yield chunk
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"❌ Error: {str(e)}"

@st.cache_resource
def get_ai_service():
    return AIService()