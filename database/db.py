"""
database/db.py — SQLite database layer for SakibAI
"""

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

DB_PATH = Path(__file__).parent.parent / "data" / "sakibai.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id          TEXT PRIMARY KEY,
                title       TEXT NOT NULL DEFAULT 'New Chat',
                model       TEXT NOT NULL DEFAULT 'llama3',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL,
                pinned      INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS messages (
                id              TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role            TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
                content         TEXT NOT NULL,
                tokens          INTEGER,
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS knowledge_docs (
                id          TEXT PRIMARY KEY,
                filename    TEXT NOT NULL,
                content     TEXT NOT NULL,
                chunk_index INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS study_sessions (
                id              TEXT PRIMARY KEY,
                source_text     TEXT NOT NULL,
                summary         TEXT,
                flashcards      TEXT,
                quiz            TEXT,
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key     TEXT PRIMARY KEY,
                value   TEXT NOT NULL
            );

            INSERT OR IGNORE INTO settings(key, value) VALUES
                ('theme', 'dark'),
                ('default_model', 'llama3'),
                ('default_temperature', '0.7'),
                ('default_max_tokens', '2048'),
                ('system_prompt', 'You are SakibAI, a highly capable, helpful, and honest AI assistant created by Sakib Hasan. You are knowledgeable, concise, and thoughtful in your responses.');
        """)


# ─── Conversations ────────────────────────────────────────────────────────────

def create_conversation(title: str = "New Chat", model: str = "llama3") -> str:
    cid = str(uuid.uuid4())
    now = _now()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversations(id, title, model, created_at, updated_at) VALUES (?,?,?,?,?)",
            (cid, title, model, now, now),
        )
    return cid


def get_conversations() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM conversations ORDER BY pinned DESC, updated_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_conversation(cid: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM conversations WHERE id=?", (cid,)).fetchone()
    return dict(row) if row else None


def update_conversation_title(cid: str, title: str) -> None:
    now = _now()
    with get_connection() as conn:
        conn.execute(
            "UPDATE conversations SET title=?, updated_at=? WHERE id=?",
            (title, now, cid),
        )


def update_conversation_model(cid: str, model: str) -> None:
    now = _now()
    with get_connection() as conn:
        conn.execute(
            "UPDATE conversations SET model=?, updated_at=? WHERE id=?",
            (model, now, cid),
        )


def toggle_pin(cid: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE conversations SET pinned = CASE WHEN pinned=1 THEN 0 ELSE 1 END WHERE id=?",
            (cid,),
        )


def delete_conversation(cid: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM conversations WHERE id=?", (cid,))


# ─── Messages ────────────────────────────────────────────────────────────────

def add_message(cid: str, role: str, content: str, tokens: Optional[int] = None) -> str:
    mid = str(uuid.uuid4())
    now = _now()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages(id, conversation_id, role, content, tokens, created_at) VALUES (?,?,?,?,?,?)",
            (mid, cid, role, content, tokens, now),
        )
        conn.execute(
            "UPDATE conversations SET updated_at=? WHERE id=?",
            (now, cid),
        )
    return mid


def get_messages(cid: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at ASC",
            (cid,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_message(mid: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE id=?", (mid,))


def clear_messages(cid: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE conversation_id=?", (cid,))


# ─── Settings ────────────────────────────────────────────────────────────────

def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def get_all_settings() -> dict:
    with get_connection() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}


# ─── Knowledge Base ───────────────────────────────────────────────────────────

def add_knowledge_doc(filename: str, chunks: list[str]) -> None:
    now = _now()
    with get_connection() as conn:
        conn.execute("DELETE FROM knowledge_docs WHERE filename=?", (filename,))
        for i, chunk in enumerate(chunks):
            conn.execute(
                "INSERT INTO knowledge_docs(id, filename, content, chunk_index, created_at) VALUES(?,?,?,?,?)",
                (str(uuid.uuid4()), filename, chunk, i, now),
            )


def search_knowledge(query: str, limit: int = 5) -> list[dict]:
    words = query.lower().split()
    if not words:
        return []
    like_clauses = " OR ".join(["LOWER(content) LIKE ?" for _ in words])
    params = [f"%{w}%" for w in words]
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM knowledge_docs WHERE {like_clauses} LIMIT ?",
            params + [limit],
        ).fetchall()
    return [dict(r) for r in rows]


def get_knowledge_files() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT filename FROM knowledge_docs ORDER BY filename"
        ).fetchall()
    return [r["filename"] for r in rows]


def delete_knowledge_file(filename: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM knowledge_docs WHERE filename=?", (filename,))


# ─── Study Sessions ──────────────────────────────────────────────────────────

def save_study_session(source_text: str, summary: str = "", flashcards: str = "", quiz: str = "") -> str:
    sid = str(uuid.uuid4())
    now = _now()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO study_sessions(id, source_text, summary, flashcards, quiz, created_at) VALUES(?,?,?,?,?,?)",
            (sid, source_text, summary, flashcards, quiz, now),
        )
    return sid


def get_study_sessions() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, source_text, created_at FROM study_sessions ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
    return [dict(r) for r in rows]


def get_study_session(sid: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM study_sessions WHERE id=?", (sid,)).fetchone()
    return dict(row) if row else None
