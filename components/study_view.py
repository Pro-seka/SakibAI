"""
components/study_view.py — Study Assistant: summarize, flashcards, quiz
"""

import json
import re
import streamlit as st
from services.ai_service import single_response
from database.db import save_study_session, get_study_sessions, get_study_session


def render_study_view() -> None:
    st.markdown('<div class="page-title">📖 Study Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Paste any text — get a summary, flashcards, and a quiz instantly.</div>',
        unsafe_allow_html=True,
    )

    tab_new, tab_history = st.tabs(["✨ New Session", "📚 History"])

    with tab_new:
        _render_new_session()

    with tab_history:
        _render_history()


def _render_new_session() -> None:
    source_text = st.text_area(
        "Paste your notes, article, or textbook excerpt:",
        height=220,
        placeholder="Paste any text here… lecture notes, Wikipedia articles, book chapters, research papers…",
        key="study_input_area",
    )

    model = st.session_state.get("selected_model", "llama3")
    word_count = len(source_text.split()) if source_text.strip() else 0
    st.caption(f"{word_count} words")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        do_summary = st.checkbox("Summary", value=True)
    with col_b:
        do_flashcards = st.checkbox("Flashcards", value=True)
    with col_c:
        do_quiz = st.checkbox("Quiz", value=True)
    with col_d:
        num_cards = st.number_input("# Cards", min_value=3, max_value=20, value=6)

    if st.button("🚀 Generate Study Materials", type="primary", use_container_width=True):
        if not source_text.strip():
            st.warning("Please paste some text first.")
            return
        if word_count < 30:
            st.warning("Please provide at least 30 words for meaningful study materials.")
            return

        result = {}

        with st.status("Generating study materials…", expanded=True) as status:
            if do_summary:
                st.write("📝 Creating summary…")
                result["summary"] = _gen_summary(source_text, model)

            if do_flashcards:
                st.write(f"🃏 Creating {num_cards} flashcards…")
                result["flashcards"] = _gen_flashcards(source_text, model, num_cards)

            if do_quiz:
                st.write("❓ Creating quiz questions…")
                result["quiz"] = _gen_quiz(source_text, model)

            status.update(label="✅ Done!", state="complete")

        st.session_state["study_result"] = result
        st.session_state["study_source"] = source_text

        save_study_session(
            source_text=source_text,
            summary=result.get("summary", ""),
            flashcards=json.dumps(result.get("flashcards", [])),
            quiz=json.dumps(result.get("quiz", [])),
        )

    result = st.session_state.get("study_result")
    if result:
        _render_result(result)


def _render_history() -> None:
    sessions = get_study_sessions()
    if not sessions:
        st.info("No study sessions yet. Generate one in the New Session tab.")
        return

    for s in sessions:
        preview = s["source_text"][:80].replace("\n", " ")
        with st.expander(f"📄 {preview}…  —  {s['created_at'][:10]}"):
            full = get_study_session(s["id"])
            if full:
                result = {}
                if full.get("summary"):
                    result["summary"] = full["summary"]
                if full.get("flashcards"):
                    try:
                        result["flashcards"] = json.loads(full["flashcards"])
                    except Exception:
                        pass
                if full.get("quiz"):
                    try:
                        result["quiz"] = json.loads(full["quiz"])
                    except Exception:
                        pass
                _render_result(result)


def _render_result(result: dict) -> None:
    st.markdown("---")

    if "summary" in result:
        st.markdown("### 📝 Summary")
        st.markdown(
            f'<div class="card card-accent">{result["summary"]}</div>',
            unsafe_allow_html=True,
        )

    if "flashcards" in result and result["flashcards"]:
        st.markdown("### 🃏 Flashcards")
        cards = result["flashcards"]
        if isinstance(cards, list):
            cols = st.columns(2)
            for i, card in enumerate(cards):
                with cols[i % 2]:
                    q = card.get("question", card.get("q", ""))
                    a = card.get("answer", card.get("a", ""))
                    st.markdown(
                        f'<div class="flashcard"><div class="fc-q">Q: {q}</div>'
                        f'<div class="fc-a">A: {a}</div></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(cards)

    if "quiz" in result and result["quiz"]:
        st.markdown("### ❓ Quiz")
        quiz = result["quiz"]
        if isinstance(quiz, list):
            for i, q in enumerate(quiz, 1):
                question = q.get("question", q.get("q", ""))
                options = q.get("options", [])
                answer = q.get("answer", q.get("a", ""))
                explanation = q.get("explanation", "")

                with st.expander(f"**Q{i}:** {question}"):
                    if options:
                        for opt in options:
                            is_correct = opt.strip().startswith(answer.strip()) or answer.strip() in opt
                            prefix = "✅ " if is_correct else "○ "
                            st.markdown(f"{prefix}{opt}")
                    else:
                        st.markdown(f"**Answer:** {answer}")
                    if explanation:
                        st.caption(f"💡 {explanation}")
        else:
            st.markdown(quiz)


# ─── AI generation helpers ───────────────────────────────────────────────────

def _gen_summary(text: str, model: str) -> str:
    prompt = (
        "Create a clear, concise summary of the following text. "
        "Use bullet points for key ideas. Keep it under 200 words.\n\n"
        f"TEXT:\n{text[:6000]}"
    )
    return single_response(prompt, model=model, temperature=0.3)


def _gen_flashcards(text: str, model: str, n: int) -> list[dict]:
    prompt = (
        f"Create exactly {n} flashcards from the text below. "
        "Return ONLY a JSON array, no explanation, no markdown fences. "
        'Each item: {"question": "...", "answer": "..."}.\n\n'
        f"TEXT:\n{text[:6000]}"
    )
    raw = single_response(prompt, model=model, temperature=0.3, max_tokens=2048)
    return _parse_json_list(raw)


def _gen_quiz(text: str, model: str) -> list[dict]:
    prompt = (
        "Create 5 multiple-choice quiz questions from the text below. "
        "Return ONLY a JSON array, no markdown, no explanation. "
        'Each item: {"question":"...", "options":["A)...","B)...","C)...","D)..."], '
        '"answer":"A", "explanation":"..."}.\n\n'
        f"TEXT:\n{text[:6000]}"
    )
    raw = single_response(prompt, model=model, temperature=0.3, max_tokens=2048)
    return _parse_json_list(raw)


def _parse_json_list(raw: str) -> list:
    # Strip markdown fences
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    # Find first [ and last ]
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1:
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            pass
    return []
