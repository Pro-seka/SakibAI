"""
components/sidebar.py — Sidebar navigation, model selector, chat history
"""

import streamlit as st
from database.db import (
    get_conversations,
    create_conversation,
    delete_conversation,
    update_conversation_title,
    toggle_pin,
    get_messages,
    get_setting,
)
from utils.session import nav_to, set_active_conversation
from providers import ALL_PROVIDERS


NAV_ITEMS = [
    ("💬", "chat",      "Chat"),
    ("📖", "study",     "Study Assistant"),
    ("📄", "pdf",       "PDF Chat"),
    ("🗂️", "knowledge", "Knowledge Base"),
    ("⚙️", "settings",  "Settings"),
]


def render_sidebar() -> None:
    with st.sidebar:
        # ── Logo ──────────────────────────────────────
        st.markdown(
            '<span class="sakibai-logo">SakibAI</span>'
            '<span class="sakibai-sub">by Sakib Hasan</span>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── New Chat button ────────────────────────────
        if st.button("＋  New Chat", use_container_width=True, type="primary"):
            _new_chat()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────
        st.markdown('<span class="sidebar-section-label">Navigation</span>', unsafe_allow_html=True)
        current_view = st.session_state.get("current_view", "chat")
        for icon, key, label in NAV_ITEMS:
            active_cls = "active" if current_view == key else ""
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
            ):
                nav_to(key)
                st.rerun()

        st.divider()

        # ── Model selector ─────────────────────────────
        _render_model_selector()

        st.divider()

        # ── Chat history ───────────────────────────────
        _render_chat_history()


def _new_chat() -> None:
    model = st.session_state.get("selected_model", "llama3")
    cid = create_conversation("New Chat", model)
    set_active_conversation(cid, [])
    st.rerun()


def _render_model_selector() -> None:
    st.markdown('<span class="sidebar-section-label">Model</span>', unsafe_allow_html=True)

    provider_options = list(ALL_PROVIDERS.keys())
    provider_labels = {
        "ollama":   "🖥️ Ollama (Local)",
        "openai":   "🤖 OpenAI",
        "groq":     "⚡ Groq",
        "together": "🌐 Together AI",
    }

    current_provider = st.session_state.get("selected_provider", "ollama")
    provider = st.selectbox(
        "Provider",
        options=provider_options,
        format_func=lambda x: provider_labels.get(x, x),
        index=provider_options.index(current_provider) if current_provider in provider_options else 0,
        key="provider_select",
        label_visibility="collapsed",
    )
    st.session_state["selected_provider"] = provider

    # Model list depends on provider
    from providers import ALL_PROVIDERS as AP
    models = AP[provider].available_models
    if not models:
        models = ["default"]

    current_model = st.session_state.get("selected_model", models[0])
    if current_model not in models:
        current_model = models[0]

    model = st.selectbox(
        "Model",
        options=models,
        index=models.index(current_model),
        key="model_select",
        label_visibility="collapsed",
    )
    st.session_state["selected_model"] = model

    # Parameters
    with st.expander("⚙️ Parameters", expanded=False):
        temp = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.get("temperature", 0.7),
            step=0.05,
            key="temp_slider",
        )
        st.session_state["temperature"] = temp

        max_tok = st.select_slider(
            "Max Tokens",
            options=[256, 512, 1024, 2048, 4096, 8192],
            value=st.session_state.get("max_tokens", 2048),
            key="maxtok_slider",
        )
        st.session_state["max_tokens"] = max_tok


def _render_chat_history() -> None:
    st.markdown('<span class="sidebar-section-label">Recent Chats</span>', unsafe_allow_html=True)

    search = st.text_input(
        "Search",
        placeholder="🔍 Search chats…",
        label_visibility="collapsed",
        key="sidebar_search_input",
    )

    conversations = get_conversations()

    if search:
        conversations = [c for c in conversations if search.lower() in c["title"].lower()]

    if not conversations:
        st.markdown(
            '<div style="color:var(--text3);font-size:0.78rem;padding:0.5rem 0.25rem">No chats yet.</div>',
            unsafe_allow_html=True,
        )
        return

    active_id = st.session_state.get("active_conversation_id")

    pinned = [c for c in conversations if c["pinned"]]
    unpinned = [c for c in conversations if not c["pinned"]]

    if pinned:
        st.markdown('<span class="sidebar-section-label" style="padding-top:0">📌 Pinned</span>', unsafe_allow_html=True)
        for conv in pinned:
            _render_conv_item(conv, active_id)

    if unpinned:
        for conv in unpinned:
            _render_conv_item(conv, active_id)


def _render_conv_item(conv: dict, active_id: str) -> None:
    cid = conv["id"]
    title = conv["title"]
    is_active = cid == active_id
    pinned = conv.get("pinned", 0)

    pin_icon = "📌" if pinned else "🗂️"
    label = f"{'▶ ' if is_active else ''}{title[:30]}{'…' if len(title) > 30 else ''}"

    col1, col2 = st.columns([5, 1])
    with col1:
        if st.button(label, key=f"conv_{cid}", use_container_width=True):
            msgs = get_messages(cid)
            set_active_conversation(cid, msgs)
            st.rerun()

    with col2:
        with st.popover("…"):
            st.markdown(f"**{title}**")
            if st.button("✏️ Rename", key=f"rename_{cid}"):
                st.session_state["edit_title_id"] = cid
                st.rerun()
            if st.button("📌 Pin/Unpin", key=f"pin_{cid}"):
                toggle_pin(cid)
                st.rerun()
            if st.button("🗑️ Delete", key=f"del_{cid}"):
                delete_conversation(cid)
                if active_id == cid:
                    st.session_state["active_conversation_id"] = None
                    st.session_state["chat_messages"] = []
                st.rerun()

    # Inline rename
    if st.session_state.get("edit_title_id") == cid:
        new_title = st.text_input(
            "New title",
            value=title,
            key=f"title_input_{cid}",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save", key=f"save_title_{cid}"):
                update_conversation_title(cid, new_title or title)
                st.session_state["edit_title_id"] = None
                st.rerun()
        with c2:
            if st.button("Cancel", key=f"cancel_title_{cid}"):
                st.session_state["edit_title_id"] = None
                st.rerun()
