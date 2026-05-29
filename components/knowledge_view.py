"""
components/knowledge_view.py — Personal Knowledge Base
"""

import streamlit as st
from services.doc_service import extract_text, chunk_text
from services.ai_service import single_response
from database.db import (
    add_knowledge_doc,
    search_knowledge,
    get_knowledge_files,
    delete_knowledge_file,
)


def render_knowledge_view() -> None:
    st.markdown('<div class="page-title">🗂️ Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Build your personal knowledge repository. Upload documents, then search and query across all of them.</div>',
        unsafe_allow_html=True,
    )

    tab_search, tab_upload, tab_manage = st.tabs(["🔍 Search & Query", "📤 Add Documents", "📋 Manage"])

    with tab_search:
        _render_search()

    with tab_upload:
        _render_upload()

    with tab_manage:
        _render_manage()


def _render_search() -> None:
    files = get_knowledge_files()
    if not files:
        st.info("📭 Your knowledge base is empty. Upload some documents in the **Add Documents** tab.")
        return

    st.markdown(f"📚 **{len(files)} document(s)** in your knowledge base")

    query = st.text_input(
        "Search your knowledge base",
        placeholder="What do you want to find?",
        key="kb_search_input",
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        ai_answer = st.toggle("🤖 AI-powered answer", value=True)
    with col2:
        max_results = st.selectbox("Results", [3, 5, 10], index=1, label_visibility="collapsed")

    if query:
        results = search_knowledge(query, limit=max_results)

        if not results:
            st.warning("No relevant content found. Try different keywords.")
            return

        if ai_answer:
            context = "\n\n---\n\n".join(
                [f"[From: {r['filename']}]\n{r['content']}" for r in results]
            )
            with st.spinner("Synthesizing answer…"):
                model = st.session_state.get("selected_model", "llama3")
                prompt = (
                    f"Based on the following knowledge base excerpts, answer this question: {query}\n\n"
                    f"EXCERPTS:\n{context}\n\n"
                    "Provide a clear, comprehensive answer based only on the provided excerpts. "
                    "Cite which document(s) the information comes from."
                )
                answer = single_response(
                    prompt,
                    system_prompt="You are SakibAI, a knowledge base assistant.",
                    model=model,
                    temperature=0.2,
                )

            st.markdown(
                f'<div class="card card-accent"><strong>🤖 AI Answer</strong><br><br>{answer}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("---")

        st.markdown(f"**📑 {len(results)} relevant excerpt(s):**")
        for i, r in enumerate(results, 1):
            with st.expander(f"Excerpt {i} — from **{r['filename']}**"):
                st.markdown(r["content"])
                st.caption(f"Chunk #{r['chunk_index']} · Added: {r['created_at'][:10]}")


def _render_upload() -> None:
    st.markdown("#### Upload documents to your knowledge base")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="kb_uploader",
    )

    chunk_size = st.slider(
        "Chunk size (words per chunk)",
        min_value=200,
        max_value=1500,
        value=800,
        step=100,
        help="Smaller chunks = more precise search. Larger = more context per result.",
    )

    if st.button("📥 Add to Knowledge Base", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Please select files first.")
            return

        for file in uploaded_files:
            with st.spinner(f"Processing {file.name}…"):
                raw = file.read()
                text = extract_text(file.name, raw)
                if "failed" in text.lower() or len(text.strip()) < 50:
                    st.error(f"❌ Could not extract text from {file.name}")
                    continue
                chunks = chunk_text(text, chunk_size=chunk_size)
                add_knowledge_doc(file.name, chunks)
                st.success(f"✅ Added **{file.name}** — {len(chunks)} chunks")

        st.balloons()


def _render_manage() -> None:
    files = get_knowledge_files()

    if not files:
        st.info("No documents in knowledge base yet.")
        return

    st.markdown(f"**{len(files)} document(s) in your knowledge base:**")

    for fname in files:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(
                f'<div class="card" style="margin-bottom:0.5rem;padding:0.75rem 1rem">'
                f'📄 {fname}</div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown("<div style='margin-top:0.75rem'>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_kb_{fname}", help=f"Delete {fname}"):
                delete_knowledge_file(fname)
                st.success(f"Deleted {fname}")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
