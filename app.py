"""
SakibAI - Enterprise AI Workspace
"""

import streamlit as st
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config.settings import DEBUG, APP_NAME
from services.chat_service import (
    init, get_messages, get_display_list, get_all_chats,
    new_chat, switch_chat, delete_chat_by_id, add_user_message, add_assistant_message,
    remove_last_message, check_and_save, get_settings,
    set_show_settings, set_export_format, set_temperature, 
    set_max_tokens, set_model, filter_for_gemini
)
from services.ai_service import get_ai_service
from utils.logger import setup_logging

logger = setup_logging()

st.set_page_config(
    page_title=f"{APP_NAME} - AI Workspace",
    page_icon="🤖",
    layout="wide"
)

def main():
    init()
    check_and_save()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ SakibAI")
        st.divider()
        
        if st.button("✨ New Chat", use_container_width=True, type="primary"):
            new_chat()
        
        st.divider()
        
        with st.expander("⚙️ Settings", expanded=get_settings()["show_settings"]):
            set_model(st.selectbox("Model", ["Gemini"], index=0))
            set_temperature(st.slider("Temperature", 0.0, 2.0, get_settings()["temperature"], 0.1))
            set_max_tokens(st.number_input("Max Tokens", 100, 8000, get_settings()["max_tokens"], 100))
            set_export_format(st.selectbox("Export Format", ["Markdown", "TXT"], index=0))
            if st.button("Close"):
                set_show_settings(False)
                st.rerun()
        
        st.divider()
        
        with st.expander("📜 Chat History", expanded=True):
            chats = get_all_chats()
            if chats:
                for chat_id, chat in chats.items():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(f"💬 {chat['name'][:30]}", key=chat_id, use_container_width=True):
                            switch_chat(chat_id)
                    with col2:
                        if st.button("🗑️", key=f"del_{chat_id}"):
                            delete_chat_by_id(chat_id)
            else:
                st.caption("No saved chats")
        
        st.divider()
        st.caption("🤖 SakibAI v4.0")
    
    # Main chat area
    st.markdown("# 🤖 SakibAI")
    st.markdown("### Your AI Workspace")
    st.divider()
    
    messages = get_messages()
    if not messages:
        st.info("👋 Welcome! Type a message below.")
    else:
        for msg in get_display_list(messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["display_time"]:
                    st.caption(f"🕐 {msg['display_time']}")
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        if add_user_message(prompt):
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                ai_service = get_ai_service()
                history = filter_for_gemini(messages)
                
                try:
                    for chunk in ai_service.stream_message(
                        message=prompt,
                        conversation_history=history,
                        temperature=get_settings()["temperature"],
                        max_tokens=get_settings()["max_tokens"]
                    ):
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    
                except Exception as e:
                    full_response = f"❌ Error: {str(e)}"
                    response_placeholder.markdown(full_response)
                
                if full_response and not full_response.startswith("❌"):
                    add_assistant_message(full_response)
                else:
                    remove_last_message()
                    st.error("Failed to get response")
        
        st.rerun()
    
    # Status bar
    with st.container():
        st.divider()
        cols = st.columns(4)
        cols[0].caption(f"🤖 {get_settings()['model']}")
        cols[1].caption(f"🌡️ Temp: {get_settings()['temperature']}")
        cols[2].caption(f"📝 Tokens: {get_settings()['max_tokens']}")
        cols[3].caption(f"💬 Messages: {len(messages)}")
    
    if DEBUG and not os.getenv("GEMINI_API_KEY"):
        st.warning("⚠️ GEMINI_API_KEY not configured")

if __name__ == "__main__":
    main()