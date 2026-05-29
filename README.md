# ⚡ SakibAI

> **Scalable AI Workspace** — A production-grade, multi-model AI platform built with Python and Streamlit.

**By Sakib Hasan

---

## What is SakibAI?

SakibAI is not a simple chatbot. It's a full AI workspace that combines:

- **Multi-provider AI chat** (Ollama, OpenAI, Groq, Together AI)
- **Document intelligence** — chat with any PDF, DOCX, or text file
- **Study assistant** — auto-generate summaries, flashcards, and quizzes
- **Personal knowledge base** — upload documents and search across them with AI
- **Full export system** — TXT, Markdown, PDF
- **Local-first & private** — SQLite database, no cloud required

Inspired by ChatGPT, Claude, NotebookLM, and Perplexity — but free, open-source, and deployable by anyone.

---

## Screenshots / Features

| Feature | Description |
|---|---|
| 💬 **Multi-turn Chat** | Streaming conversations with full context, auto-title generation |
| 🧠 **Multi-Provider** | Switch between Ollama (free, local), OpenAI, Groq, Together AI |
| 📖 **Study Assistant** | Paste any text → instant summary + flashcards + quiz |
| 📄 **PDF Chat** | Upload a doc, ask questions — AI answers from document content |
| 🗂️ **Knowledge Base** | Build a personal repository, search with AI synthesis |
| 📤 **Export** | Download any conversation as TXT, Markdown, or PDF |
| 🔒 **Private** | Everything stored locally in SQLite, API keys never leave your machine |
| ⚙️ **Configurable** | Custom system prompts, temperature, max tokens, provider presets |

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/sakibhasan/sakibai.git
cd sakibai
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up a model provider

**Option A — Ollama (Recommended, free, local)**

```bash
# Install Ollama from https://ollama.ai
ollama pull llama3        # Download a model (~4GB)
ollama serve              # Start the Ollama server
```

**Option B — API keys (OpenAI, Groq, Together AI)**

```bash
cp .env.example .env
# Edit .env and add your API keys
# OR add them through the Settings UI in the app
```

### 5. Run SakibAI

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` — you're good to go! ⚡

---

## Project Structure

```
SakibAI/
│
├── app.py                    # Entry point
│
├── components/               # UI components (one per view)
│   ├── sidebar.py            # Navigation, model selector, chat history
│   ├── chat_view.py          # Main chat interface
│   ├── study_view.py         # Study assistant
│   ├── pdf_view.py           # PDF / document chat
│   ├── knowledge_view.py     # Knowledge base
│   └── settings_view.py      # Settings panel
│
├── services/                 # Business logic layer
│   ├── ai_service.py         # AI orchestration (streaming, single response)
│   ├── export_service.py     # TXT / MD / PDF export
│   └── doc_service.py        # Document parsing + chunking
│
├── providers/                # AI provider adapters
│   ├── base.py               # Abstract base class
│   ├── ollama_provider.py    # Ollama (local)
│   └── openai_provider.py    # OpenAI, Groq, Together AI
│
├── database/                 # Data layer
│   └── db.py                 # SQLite operations (conversations, messages, KB)
│
├── utils/                    # Shared utilities
│   ├── session.py            # Streamlit session state management
│   └── styles.py             # All custom CSS
│
├── data/                     # SQLite database (auto-created, gitignored)
├── .streamlit/config.toml    # Streamlit theme config
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Supported AI Providers

| Provider | Models | Cost | Setup |
|---|---|---|---|
| **Ollama** | llama3, mistral, gemma, qwen, codellama, phi3, deepseek-coder + more | 🆓 Free | Install ollama + pull model |
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo | 💳 Paid | API key |
| **Groq** | llama3-70b, llama3-8b, mixtral-8x7b, gemma2 | 🆓 Free tier | API key |
| **Together AI** | llama3-70b/8b, mixtral, mistral, qwen2 | 🆓 Free tier | API key |

---

## Deployment

### Local (Development)

```bash
streamlit run app.py
```

### Streamlit Cloud (Free hosting)

1. Push your repo to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and deploy
4. Add API keys via Streamlit Cloud Secrets

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t sakibai .
docker run -p 8501:8501 sakibai
```

---

## Architecture

```
User (Browser)
       ↓
   Streamlit UI
       ↓
  Components Layer          ← Views: chat, study, pdf, knowledge, settings
       ↓
  Services Layer            ← AI orchestration, document parsing, export
       ↓
  Providers Layer           ← Ollama, OpenAI, Groq, Together AI adapters
       ↓
  Database Layer            ← SQLite (conversations, messages, KB, settings)
       ↓
  AI APIs / Local Models
```

**Design Principles:**
- **Separation of concerns** — each layer has one job
- **Provider independence** — swap AI backends without touching UI code
- **Zero build step** — no webpack, no bundler, runs with `streamlit run`
- **Single file DB** — SQLite requires no server setup
- **Type hints everywhere** — every function annotated

---

## Adding a New Provider

1. Create `providers/my_provider.py`:

```python
from .base import BaseProvider
from typing import Iterator

class MyProvider(BaseProvider):
    name = "myprovider"
    display_name = "My Provider"
    available_models = ["model-1", "model-2"]

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages, model, temperature=0.7, max_tokens=2048, stream=True) -> Iterator[str]:
        # Your implementation here
        yield "response token by token"
```

2. Register it in `providers/__init__.py`:

```python
from .my_provider import MyProvider
ALL_PROVIDERS["myprovider"] = MyProvider
```

That's it — it automatically appears in the sidebar model selector.

---

## Engineering Standards

- ✅ Type hints on every function
- ✅ Docstrings on public modules and functions
- ✅ Modular architecture — components, services, providers, database
- ✅ Database migrations handled via `CREATE TABLE IF NOT EXISTS`
- ✅ No hardcoded API keys — stored in DB or `.env`
- ✅ Streaming responses with real-time token display
- ✅ Error handling on all AI calls with user-friendly messages
- ✅ Feature branches + meaningful commit messages (recommended)

---

## Roadmap

### v1.1
- [ ] Web search integration (Tavily / SerpAPI)
- [ ] Voice input (Web Speech API)
- [ ] DOCX export

### v1.2
- [ ] Vector database (ChromaDB / Qdrant) for semantic KB search
- [ ] Multi-PDF knowledge base with folder organization
- [ ] Conversation branching

### v2.0
- [ ] User authentication (OAuth)
- [ ] Multi-user support
- [ ] Cloud sync
- [ ] Plugin system

---

## License

MIT — free to use, modify, and distribute.

---

## Credits

Built by **Sakib Hasan** as a production-grade AI workspace demonstrating:
- Professional Python software architecture
- Multi-provider AI integration patterns
- Full-stack Streamlit application design
- Local-first, privacy-respecting AI tooling

---

*"AI Assistant is not intended to be a simple chatbot. It is designed as a scalable AI workspace that evolves from a conversational assistant into a document-aware, knowledge-driven productivity platform."*

**— SakibAI Vision Document v1.0**
