"""
components/settings_view.py — Application settings panel
"""

import streamlit as st
from database.db import get_all_settings, set_setting, get_setting


def render_settings_view() -> None:
    st.markdown('<div class="page-title">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Configure SakibAI to your preferences.</div>',
        unsafe_allow_html=True,
    )

    settings = get_all_settings()

    tab_general, tab_providers, tab_system, tab_about = st.tabs(
        ["🎛️ General", "🔑 API Keys", "🤖 System Prompt", "ℹ️ About"]
    )

    with tab_general:
        _render_general(settings)

    with tab_providers:
        _render_providers(settings)

    with tab_system:
        _render_system_prompt(settings)

    with tab_about:
        _render_about()


def _render_general(settings: dict) -> None:
    st.markdown("#### General Preferences")

    default_model = st.text_input(
        "Default model",
        value=settings.get("default_model", "llama3"),
        help="Model name to use by default when starting a new chat",
    )

    default_temp = st.slider(
        "Default temperature",
        0.0, 2.0,
        float(settings.get("default_temperature", "0.7")),
        0.05,
    )

    default_tokens = st.select_slider(
        "Default max tokens",
        options=[256, 512, 1024, 2048, 4096, 8192],
        value=int(settings.get("default_max_tokens", "2048")),
    )

    if st.button("💾 Save General Settings", type="primary"):
        set_setting("default_model", default_model)
        set_setting("default_temperature", str(default_temp))
        set_setting("default_max_tokens", str(default_tokens))

        # Update session state too
        st.session_state["selected_model"] = default_model
        st.session_state["temperature"] = default_temp
        st.session_state["max_tokens"] = default_tokens

        st.success("✅ Settings saved!")


def _render_providers(settings: dict) -> None:
    st.markdown("#### API Keys")
    st.info(
        "💡 API keys are stored locally in your SQLite database and never sent anywhere except the respective AI provider.",
        icon="🔒",
    )

    # Ollama
    with st.expander("🖥️ Ollama (Local — Free)", expanded=True):
        st.markdown(
            "Ollama runs models locally on your machine — **completely free and private**.\n\n"
            "1. Install from [ollama.ai](https://ollama.ai)\n"
            "2. Run `ollama pull llama3` in terminal\n"
            "3. Run `ollama serve`"
        )
        if st.button("🔄 Test Ollama Connection", key="test_ollama"):
            from providers.ollama_provider import OllamaProvider
            p = OllamaProvider()
            if p.is_available():
                models = p.get_local_models()
                st.success(f"✅ Connected! Local models: {', '.join(models) or 'none pulled yet'}")
            else:
                st.error("❌ Ollama not running. Start with `ollama serve`")

    # OpenAI
    with st.expander("🤖 OpenAI"):
        openai_key = st.text_input(
            "OpenAI API Key",
            value=settings.get("openai_api_key", ""),
            type="password",
            placeholder="sk-...",
        )
        if st.button("Save OpenAI Key"):
            set_setting("openai_api_key", openai_key)
            st.success("✅ Saved!")

    # Groq
    with st.expander("⚡ Groq (Fast & Free tier)"):
        st.markdown("Get a free API key at [console.groq.com](https://console.groq.com)")
        groq_key = st.text_input(
            "Groq API Key",
            value=settings.get("groq_api_key", ""),
            type="password",
            placeholder="gsk_...",
        )
        if st.button("Save Groq Key"):
            set_setting("groq_api_key", groq_key)
            st.success("✅ Saved!")

    # Together AI
    with st.expander("🌐 Together AI"):
        st.markdown("Get a key at [api.together.xyz](https://api.together.xyz)")
        together_key = st.text_input(
            "Together AI Key",
            value=settings.get("together_api_key", ""),
            type="password",
        )
        if st.button("Save Together Key"):
            set_setting("together_api_key", together_key)
            st.success("✅ Saved!")

    # Active provider
    st.markdown("---")
    st.markdown("#### Active Provider")
    provider = st.selectbox(
        "Default provider",
        options=["ollama", "openai", "groq", "together"],
        index=["ollama", "openai", "groq", "together"].index(
            settings.get("provider", "ollama")
        ),
        format_func=lambda x: {
            "ollama": "🖥️ Ollama (Local)",
            "openai": "🤖 OpenAI",
            "groq": "⚡ Groq",
            "together": "🌐 Together AI",
        }[x],
    )
    if st.button("Save Active Provider", type="primary"):
        set_setting("provider", provider)
        st.session_state["selected_provider"] = provider
        st.success(f"✅ Active provider set to {provider}")


def _render_system_prompt(settings: dict) -> None:
    st.markdown("#### System Prompt")
    st.markdown(
        "The system prompt defines SakibAI's personality and behavior. "
        "It's sent at the start of every conversation."
    )

    system_prompt = st.text_area(
        "System prompt",
        value=settings.get(
            "system_prompt",
            "You are SakibAI, a highly capable, helpful, and honest AI assistant created by Sakib Hasan.",
        ),
        height=200,
        label_visibility="collapsed",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save System Prompt", type="primary", use_container_width=True):
            set_setting("system_prompt", system_prompt)
            st.session_state["system_prompt"] = system_prompt
            st.success("✅ Saved!")
    with col2:
        if st.button("↩️ Reset to Default", use_container_width=True):
            default = "You are SakibAI, a highly capable, helpful, and honest AI assistant created by Sakib Hasan. You are knowledgeable, concise, and thoughtful in your responses."
            set_setting("system_prompt", default)
            st.session_state["system_prompt"] = default
            st.rerun()

    st.markdown("**Presets:**")
    presets = {
        "🤖 Default": "You are SakibAI, a highly capable, helpful, and honest AI assistant created by Sakib Hasan. You are knowledgeable, concise, and thoughtful in your responses.",
        "👨‍💻 Coding Expert": "You are SakibAI, an expert software engineer. Provide precise, production-quality code with explanations. Always consider edge cases, performance, and best practices.",
        "🎓 Tutor": "You are SakibAI, a patient and encouraging tutor. Explain concepts clearly with examples, check understanding, and adapt your explanations to the learner's level.",
        "✍️ Writing Assistant": "You are SakibAI, a skilled writing assistant. Help with clarity, structure, tone, and style. Provide constructive feedback and suggest improvements.",
        "🔬 Research Assistant": "You are SakibAI, a research assistant. Help analyze information, synthesize findings, identify patterns, and present data clearly. Always note limitations and uncertainties.",
    }
    for name, prompt in presets.items():
        if st.button(name, key=f"preset_{name}"):
            set_setting("system_prompt", prompt)
            st.session_state["system_prompt"] = prompt
            st.success(f"✅ Applied preset: {name}")
            st.rerun()


def _render_about() -> None:
    st.markdown(
        """
<div style="text-align:center;padding:2rem 0">
    <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;
                background:linear-gradient(135deg,#7c6af7,#a78bfa,#c4b5fd);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;letter-spacing:-0.02em;margin-bottom:0.25rem">
        SakibAI
    </div>
    <div style="color:var(--text2);font-size:0.9rem">Scalable AI Workspace · v1.0.0</div>
    <div style="color:var(--text3);font-size:0.8rem;margin-top:0.25rem">by Sakib Hasan, Lead Director</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    cols = st.columns(3)
    modules = [
        ("💬", "Multi-turn Chat", "Streaming conversations with context"),
        ("🧠", "Multi-Provider", "Ollama, OpenAI, Groq, Together AI"),
        ("📖", "Study Assistant", "Summaries, flashcards, quizzes"),
        ("📄", "PDF Chat", "Ask questions about documents"),
        ("🗂️", "Knowledge Base", "Build a personal document repository"),
        ("📤", "Export", "TXT, Markdown, PDF formats"),
        ("🔒", "Private", "Local SQLite, no data leaves your machine"),
        ("⚙️", "Configurable", "System prompts, parameters, providers"),
        ("🆓", "Open Source", "Free, self-hostable, yours to modify"),
    ]
    for i, (icon, title, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(
                f'<div class="card" style="text-align:center;padding:1rem">'
                f'<div style="font-size:1.5rem">{icon}</div>'
                f'<div style="font-weight:600;margin:0.4rem 0 0.2rem;font-size:0.85rem">{title}</div>'
                f'<div style="color:var(--text2);font-size:0.75rem">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        """
**Tech Stack:**
- **Frontend:** Streamlit + custom CSS
- **AI Providers:** Ollama, OpenAI, Groq, Together AI
- **Database:** SQLite (local, zero configuration)
- **Document Parsing:** pdfplumber / pypdf, python-docx
- **Export:** reportlab (PDF), built-in MD/TXT
- **Architecture:** Modular providers → services → components

**Built with ❤️ by Sakib Hasan**
"""
    )
