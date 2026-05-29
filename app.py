"""
SakibAI — Scalable AI Workspace
Author: Sakib Hasan, Lead Director
Version: 1.0.0
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from components.sidebar import render_sidebar
from components.chat_view import render_chat_view
from components.study_view import render_study_view
from components.pdf_view import render_pdf_view
from components.knowledge_view import render_knowledge_view
from components.settings_view import render_settings_view
from database.db import init_db
from utils.session import init_session_state
from utils.styles import inject_styles


def main() -> None:
    st.set_page_config(
        page_title="SakibAI",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/sakibhasan/sakibai",
            "About": "SakibAI — Scalable AI Workspace by Sakib Hasan",
        },
    )

    init_db()
    init_session_state()
    inject_styles()

    render_sidebar()

    view = st.session_state.get("current_view", "chat")

    if view == "chat":
        render_chat_view()
    elif view == "study":
        render_study_view()
    elif view == "pdf":
        render_pdf_view()
    elif view == "knowledge":
        render_knowledge_view()
    elif view == "settings":
        render_settings_view()


if __name__ == "__main__":
    main()
