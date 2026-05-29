"""
utils/styles.py — All custom CSS for SakibAI
"""

import streamlit as st


def inject_styles() -> None:
    st.markdown("""
<style>
/* ── Fonts ──────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ── Root Variables ─────────────────────────────── */
:root {
    --bg:          #0a0a0f;
    --surface:     #111118;
    --surface2:    #16161f;
    --surface3:    #1e1e2a;
    --border:      rgba(255,255,255,0.07);
    --border2:     rgba(255,255,255,0.12);
    --accent:      #7c6af7;
    --accent2:     #5e4bdb;
    --accent-glow: rgba(124,106,247,0.25);
    --text:        #e8e8f0;
    --text2:       #9898b0;
    --text3:       #5a5a72;
    --user-bg:     rgba(124,106,247,0.12);
    --ai-bg:       rgba(255,255,255,0.03);
    --success:     #4ade80;
    --warning:     #f59e0b;
    --error:       #f87171;
    --radius:      12px;
    --radius-sm:   8px;
    --font-ui:     'Syne', sans-serif;
    --font-body:   'DM Sans', sans-serif;
    --font-mono:   'DM Mono', monospace;
}

/* ── Base Reset ─────────────────────────────────── */
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* ── Hide Streamlit chrome ──────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.stDecoration { display: none; }

/* ── App layout ─────────────────────────────────── */
.main .block-container {
    padding: 1.5rem 2rem 5rem 2rem !important;
    max-width: 900px !important;
}

/* ── Sidebar ────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* ── Logo in sidebar ────────────────────────────── */
.sakibai-logo {
    font-family: var(--font-ui) !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #7c6af7, #a78bfa, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 1rem 0 0.25rem 0;
    display: block;
}
.sakibai-sub {
    font-size: 0.68rem !important;
    color: var(--text3) !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: var(--font-mono) !important;
    -webkit-text-fill-color: var(--text3);
}

/* ── Nav buttons ────────────────────────────────── */
.nav-btn {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.55rem 0.75rem;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-family: var(--font-body);
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text2) !important;
    transition: all 0.15s ease;
    border: none;
    background: transparent;
    width: 100%;
    text-align: left;
    margin-bottom: 2px;
}
.nav-btn:hover { background: var(--surface3); color: var(--text) !important; }
.nav-btn.active { background: var(--user-bg); color: var(--accent) !important; }

/* ── Chat history items ─────────────────────────── */
.chat-item {
    padding: 0.45rem 0.75rem;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 0.8rem;
    color: var(--text2) !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: all 0.15s ease;
    margin-bottom: 1px;
}
.chat-item:hover { background: var(--surface3); color: var(--text) !important; }
.chat-item.pinned { border-left: 2px solid var(--accent); padding-left: 0.6rem; }

/* ── Section labels in sidebar ──────────────────── */
.sidebar-section-label {
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text3) !important;
    -webkit-text-fill-color: var(--text3);
    padding: 0.75rem 0 0.35rem 0.1rem;
    display: block;
}

/* ── Chat messages ──────────────────────────────── */
.message-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    padding-bottom: 2rem;
}

.message-user {
    display: flex;
    justify-content: flex-end;
}
.message-user .bubble {
    background: var(--user-bg);
    border: 1px solid rgba(124,106,247,0.2);
    border-radius: 18px 18px 4px 18px;
    padding: 0.85rem 1.1rem;
    max-width: 78%;
    font-size: 0.9rem;
    line-height: 1.6;
}

.message-ai {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}
.message-ai .avatar {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--accent), #a78bfa);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
    margin-top: 4px;
    box-shadow: 0 0 12px var(--accent-glow);
    color: white !important;
    -webkit-text-fill-color: white;
    font-weight: 700;
    font-family: var(--font-ui);
}
.message-ai .bubble {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-radius: 4px 18px 18px 18px;
    padding: 0.85rem 1.1rem;
    font-size: 0.9rem;
    line-height: 1.7;
    flex: 1;
}

/* ── Code blocks ────────────────────────────────── */
.message-ai pre, .message-user pre {
    background: var(--surface3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius-sm) !important;
    padding: 1rem !important;
    overflow-x: auto !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}
code {
    font-family: var(--font-mono) !important;
    background: var(--surface3) !important;
    padding: 0.15em 0.4em !important;
    border-radius: 4px !important;
    font-size: 0.85em !important;
}

/* ── Input area ─────────────────────────────────── */
.stChatInputContainer, [data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 16px !important;
    padding: 0.25rem 0.5rem !important;
}
.stChatInputContainer:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── Streamlit text area ────────────────────────── */
.stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── Streamlit inputs ───────────────────────────── */
.stTextInput input, .stSelectbox select {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* ── Buttons ────────────────────────────────────── */
.stButton button {
    background: var(--surface3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease !important;
}
.stButton button:hover {
    background: var(--surface2) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    border: none !important;
    color: white !important;
}

/* ── Sliders ────────────────────────────────────── */
.stSlider [data-baseweb="slider"] {
    padding: 0.5rem 0 !important;
}
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--accent) !important;
}

/* ── Tabs ───────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface2) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text2) !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface3) !important;
    color: var(--text) !important;
}

/* ── Expanders ──────────────────────────────────── */
.stExpander {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Alerts ─────────────────────────────────────── */
.stAlert {
    border-radius: var(--radius) !important;
    border: none !important;
}

/* ── Page titles ────────────────────────────────── */
.page-title {
    font-family: var(--font-ui) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    color: var(--text) !important;
    margin-bottom: 0.25rem;
}
.page-subtitle {
    font-size: 0.85rem !important;
    color: var(--text2) !important;
    margin-bottom: 1.5rem;
}

/* ── Cards ──────────────────────────────────────── */
.card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    margin-bottom: 0.75rem;
}
.card-accent {
    border-left: 3px solid var(--accent);
}

/* ── Metric cards ───────────────────────────────── */
.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
.metric-label {
    font-size: 0.7rem;
    color: var(--text3);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: var(--font-mono);
}
.metric-value {
    font-size: 1.4rem;
    font-weight: 700;
    font-family: var(--font-ui);
    color: var(--text);
}

/* ── Flashcards ─────────────────────────────────── */
.flashcard {
    background: var(--surface2);
    border: 1px solid var(--border2);
    border-radius: var(--radius);
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    position: relative;
    transition: all 0.2s ease;
}
.flashcard:hover {
    border-color: var(--accent);
    box-shadow: 0 0 20px var(--accent-glow);
    transform: translateY(-1px);
}
.flashcard .fc-q {
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
.flashcard .fc-a {
    color: var(--text2);
    font-size: 0.85rem;
    border-top: 1px solid var(--border);
    padding-top: 0.5rem;
    margin-top: 0.5rem;
}

/* ── Tag pill ───────────────────────────────────── */
.tag {
    display: inline-block;
    padding: 0.2em 0.65em;
    border-radius: 100px;
    font-size: 0.7rem;
    font-weight: 600;
    background: var(--user-bg);
    color: var(--accent);
    border: 1px solid rgba(124,106,247,0.3);
    font-family: var(--font-mono);
    letter-spacing: 0.04em;
}

/* ── Welcome screen ─────────────────────────────── */
.welcome-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    margin-top: 2rem;
}
.welcome-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    cursor: pointer;
    transition: all 0.2s ease;
}
.welcome-card:hover {
    border-color: var(--accent);
    background: var(--surface3);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.welcome-card .wc-icon { font-size: 1.25rem; margin-bottom: 0.4rem; }
.welcome-card .wc-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.2rem;
}
.welcome-card .wc-desc { font-size: 0.75rem; color: var(--text2); }

/* ── Scrollbar ──────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text3); }

/* ── Dividers ───────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Select boxes ───────────────────────────────── */
[data-baseweb="select"] > div {
    background: var(--surface2) !important;
    border-color: var(--border2) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Upload box ─────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}

/* ── Progress bar ───────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent), #a78bfa) !important;
}

/* ── Spinner ────────────────────────────────────── */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ── Streamlit columns gap fix ──────────────────── */
[data-testid="column"] { padding: 0 0.4rem !important; }

/* ── Markdown in chat ───────────────────────────── */
.bubble p { margin: 0.4em 0 !important; }
.bubble h1, .bubble h2, .bubble h3 {
    font-family: var(--font-ui) !important;
    font-weight: 700 !important;
    margin: 0.75em 0 0.35em 0 !important;
}
.bubble ul, .bubble ol { padding-left: 1.25em !important; }
.bubble li { margin: 0.25em 0 !important; }
.bubble table {
    border-collapse: collapse !important;
    width: 100% !important;
    font-size: 0.85em !important;
}
.bubble th, .bubble td {
    border: 1px solid var(--border2) !important;
    padding: 0.5em 0.75em !important;
}
.bubble th { background: var(--surface3) !important; }
</style>
""", unsafe_allow_html=True)
