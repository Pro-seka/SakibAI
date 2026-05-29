"""
components/chat_view.py — Main chat interface
"""

import streamlit as st
from database.db import (
    create_conversation,
    add_message,
    get_messages,
    update_conversation_title,
    get_conversation,
    get_setting,
    clear_messages,
)
from services.ai_service import stream_response, generate_title
from services.export_service import to_markdown, to_txt, to_pdf_bytes
from utils.session import set_active_conversation

STARTER_PROMPTS = [
    ("💡", "Explain a concept", "Explain quantum entanglement in simple terms"),
    ("🐛", "Debug my code", "Help me find the bug in this Python function"),
    ("✍️", "Write something", "Write a professional email declining a meeting"),
    ("📊", "Analyze data", "How do I calculate the correlation between two variables?"),
    ("🗺️", "Plan something", "Help me plan a 7-day study schedule for final exams"),
    ("🤔", "Think through it", "What are the pros and cons of microservices vs monolith?"),
]


def render_chat_view() -> None:
    cid = st.session_state.get("active_conversation_id")

    # No conversation selected → show welcome screen
    if cid is None:
        _render_welcome()
        return

    # Verify conversation still exists
    conv = get_conversation(cid)
    if conv is None:
        st.session_state["active_conversation_id"] = None
        st.session_state["chat_messages"] = []
        _render_welcome()
        return

    _render_chat_header(conv)
    _render_messages()
    _render_input(cid, conv)


def _render_welcome() -> None:
    st.markdown(
        """
<div style="text-align:center;padding:3rem 0 1rem 0">
    <div style="font-size:2.5rem;margin-bottom:0.5rem">⚡</div>
    <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                background:linear-gradient(135deg,#7c6af7,#a78bfa,#c4b5fd);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;letter-spacing:-0.02em">
        Welcome to SakibAI
    </div>
    <div style="color:var(--text2);font-size:0.9rem;margin-top:0.4rem">
        Your intelligent workspace. Start a conversation or pick a prompt below.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Starter prompt grid
    cols = st.columns(2)
    for i, (icon, title, prompt) in enumerate(STARTER_PROMPTS):
        with cols[i % 2]:
            if st.button(
                f"{icon} **{title}**\n\n*{prompt}*",
                key=f"starter_{i}",
                use_container_width=True,
            ):
                _start_with_prompt(prompt)


def _start_with_prompt(prompt: str) -> None:
    model = st.session_state.get("selected_model", "llama3")
    cid = create_conversation("New Chat", model)
    set_active_conversation(cid, [])
    st.session_state["pending_starter_prompt"] = prompt
    st.rerun()


def _render_chat_header(conv: dict) -> None:
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1:
        st.markdown(
            f'<div class="page-title" style="margin-bottom:0">{conv["title"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="font-size:0.72rem;color:var(--text3);font-family:\'DM Mono\',monospace">'
            f'model: {conv["model"]}  ·  {len(st.session_state.get("chat_messages",[]))} messages</div>',
            unsafe_allow_html=True,
        )
    with c2:
        _render_export_button(conv)
    with c3:
        if st.button("🗑️ Clear", use_container_width=True):
            clear_messages(conv["id"])
            st.session_state["chat_messages"] = []
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def _render_export_button(conv: dict) -> None:
    msgs = st.session_state.get("chat_messages", [])
    if not msgs:
        return

    with st.popover("📤 Export"):
        st.markdown("**Export conversation**")

        md = to_markdown(conv["title"], msgs)
        st.download_button(
            "📝 Markdown (.md)",
            data=md,
            file_name=f"{conv['title'][:30]}.md",
            mime="text/markdown",
            use_container_width=True,
        )

        txt = to_txt(conv["title"], msgs)
        st.download_button(
            "📄 Plain text (.txt)",
            data=txt,
            file_name=f"{conv['title'][:30]}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        pdf = to_pdf_bytes(conv["title"], msgs)
        if pdf:
            st.download_button(
                "📕 PDF (.pdf)",
                data=pdf,
                file_name=f"{conv['title'][:30]}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.caption("Install `reportlab` for PDF export")


def _render_messages() -> None:
    messages = st.session_state.get("chat_messages", [])
    if not messages:
        return

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            continue

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="⚡"):
                st.markdown(content)


def _render_input(cid: str, conv: dict) -> None:
    # Handle starter prompt injection
    pending = st.session_state.pop("pending_starter_prompt", None)

    system_prompt = st.session_state.get("system_prompt", get_setting("system_prompt", ""))
    model = st.session_state.get("selected_model", conv.get("model", "llama3"))
    temperature = st.session_state.get("temperature", 0.7)
    max_tokens = st.session_state.get("max_tokens", 2048)

    if pending:
        user_input = pending
    else:
        user_input = st.chat_input("Message SakibAI…", key="main_chat_input")

    if not user_input:
        return

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Persist user message
    add_message(cid, "user", user_input)
    msgs_history = st.session_state.get("chat_messages", [])
    msgs_history.append({"role": "user", "content": user_input})
    st.session_state["chat_messages"] = msgs_history

    # Build message history for the LLM (exclude system, raw role/content only)
    llm_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in msgs_history
        if m["role"] in ("user", "assistant")
    ]

    # Stream AI response
    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        full_response = ""
        try:
            for token in stream_response(
                messages=llm_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
            ):
                full_response += token
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"⚠️ Error: {e}"
            placeholder.error(full_response)

    # Persist AI message
    add_message(cid, "assistant", full_response)
    msgs_history.append({"role": "assistant", "content": full_response})
    st.session_state["chat_messages"] = msgs_history

    # Auto-generate title for first user message
    if len([m for m in msgs_history if m["role"] == "user"]) == 1:
        try:
            title = generate_title(user_input)
            update_conversation_title(cid, title)
        except Exception:
            pass

    st.rerun()
