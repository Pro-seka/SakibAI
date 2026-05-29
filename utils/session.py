"""
utils/session.py — Streamlit session state management
"""

import streamlit as st
from database.db import get_all_settings


def init_session_state() -> None:
    """Initialize all session state keys with sensible defaults."""
    settings = get_all_settings()

    defaults = {
        # Navigation
        "current_view": "chat",
        # Active conversation
        "active_conversation_id": None,
        "chat_messages": [],
        # Model config (from DB settings)
        "selected_provider": settings.get("provider", "ollama"),
        "selected_model": settings.get("default_model", "llama3"),
        "temperature": float(settings.get("default_temperature", "0.7")),
        "max_tokens": int(settings.get("default_max_tokens", "2048")),
        "system_prompt": settings.get("system_prompt", "You are SakibAI, a helpful AI assistant."),
        # UI state
        "sidebar_search": "",
        "edit_title_id": None,
        # Study session
        "study_text": "",
        "study_result": None,
        # PDF chat
        "pdf_text": "",
        "pdf_filename": "",
        "pdf_messages": [],
        # Knowledge base
        "kb_query": "",
        # Streaming
        "is_streaming": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def nav_to(view: str) -> None:
    st.session_state["current_view"] = view


def set_active_conversation(cid: str, messages: list[dict]) -> None:
    st.session_state["active_conversation_id"] = cid
    st.session_state["chat_messages"] = messages
    st.session_state["current_view"] = "chat"
