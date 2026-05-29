"""
components/pdf_view.py — Chat with any PDF / document
"""

import streamlit as st
from services.ai_service import single_response
from services.doc_service import extract_text, truncate_for_context


def render_pdf_view() -> None:
    st.markdown('<div class="page-title">📄 PDF Chat</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Upload any PDF, DOCX, or text file and ask questions about it.</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 2])

    with col_left:
        _render_upload_panel()

    with col_right:
        _render_chat_panel()


def _render_upload_panel() -> None:
    st.markdown("#### 📁 Document")

    uploaded = st.file_uploader(
        "Upload document",
        type=["pdf", "docx", "txt", "md", "py", "js", "ts", "html", "css", "json", "csv"],
        label_visibility="collapsed",
        key="pdf_uploader",
    )

    if uploaded:
        with st.spinner(f"Reading {uploaded.name}…"):
            raw_bytes = uploaded.read()
            text = extract_text(uploaded.name, raw_bytes)

        if "[" in text and "failed" in text.lower():
            st.error(text)
            return

        st.session_state["pdf_text"] = text
        st.session_state["pdf_filename"] = uploaded.name
        st.session_state["pdf_messages"] = []

        word_count = len(text.split())
        char_count = len(text)

        st.success(f"✅ Loaded: **{uploaded.name}**")

        st.markdown(
            f"""
<div class="card" style="margin-top:0.75rem">
    <div class="metric-label">Document stats</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem">
        <div>
            <div class="metric-label">Words</div>
            <div style="font-weight:600;font-size:1.1rem">{word_count:,}</div>
        </div>
        <div>
            <div class="metric-label">Characters</div>
            <div style="font-weight:600;font-size:1.1rem">{char_count:,}</div>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        with st.expander("📄 Preview text"):
            st.text(text[:1500] + ("…" if len(text) > 1500 else ""))

        # Quick question starters
        st.markdown("**Quick questions:**")
        quick = [
            "Summarize this document",
            "What are the main points?",
            "List the key takeaways",
            "What questions does this answer?",
        ]
        for q in quick:
            if st.button(q, key=f"quick_{q}", use_container_width=True):
                _send_pdf_message(q)

    elif not st.session_state.get("pdf_text"):
        st.markdown(
            """
<div style="text-align:center;padding:2rem 1rem;border:1px dashed var(--border2);
            border-radius:12px;color:var(--text3)">
    <div style="font-size:2rem;margin-bottom:0.5rem">📂</div>
    <div style="font-size:0.85rem">Upload a document to begin</div>
    <div style="font-size:0.75rem;margin-top:0.3rem">PDF, DOCX, TXT, MD, code files…</div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        fname = st.session_state.get("pdf_filename", "document")
        st.success(f"✅ Active: **{fname}**")
        if st.button("🗑️ Clear document", use_container_width=True):
            st.session_state["pdf_text"] = ""
            st.session_state["pdf_filename"] = ""
            st.session_state["pdf_messages"] = []
            st.rerun()


def _render_chat_panel() -> None:
    pdf_text = st.session_state.get("pdf_text", "")

    if not pdf_text:
        st.markdown(
            """
<div style="display:flex;align-items:center;justify-content:center;height:400px;
            color:var(--text3);font-size:0.9rem;text-align:center">
    <div>
        <div style="font-size:3rem;margin-bottom:1rem">👈</div>
        Upload a document on the left to start chatting with it
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    st.markdown(f"#### 💬 Chat with {st.session_state.get('pdf_filename','document')}")

    # Render message history
    pdf_messages = st.session_state.get("pdf_messages", [])
    for msg in pdf_messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="⚡"):
                st.markdown(content)

    # Chat input
    user_q = st.chat_input("Ask anything about the document…", key="pdf_chat_input")
    if user_q:
        _send_pdf_message(user_q)


def _send_pdf_message(question: str) -> None:
    pdf_text = st.session_state.get("pdf_text", "")
    model = st.session_state.get("selected_model", "llama3")
    pdf_messages = st.session_state.get("pdf_messages", [])

    pdf_messages.append({"role": "user", "content": question})
    st.session_state["pdf_messages"] = pdf_messages

    context = truncate_for_context(pdf_text, max_chars=8000)

    # Build chat history for context
    history_str = ""
    for m in pdf_messages[-6:]:  # last 3 turns
        if m["role"] == "user":
            history_str += f"User: {m['content']}\n"
        elif m["role"] == "assistant":
            history_str += f"Assistant: {m['content']}\n"

    system = (
        "You are SakibAI, a document analysis assistant. "
        "Answer questions based ONLY on the provided document content. "
        "If the answer isn't in the document, say so clearly. "
        "Be precise, cite relevant sections when helpful."
    )

    prompt = (
        f"DOCUMENT CONTENT:\n{context}\n\n"
        f"CONVERSATION HISTORY:\n{history_str}\n"
        f"QUESTION: {question}"
    )

    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        full_response = ""
        from services.ai_service import get_active_provider
        provider = get_active_provider()
        messages_for_llm = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        for token in provider.chat(
            messages=messages_for_llm,
            model=model,
            temperature=0.2,
            max_tokens=2048,
        ):
            full_response += token
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    pdf_messages.append({"role": "assistant", "content": full_response})
    st.session_state["pdf_messages"] = pdf_messages
    st.rerun()
