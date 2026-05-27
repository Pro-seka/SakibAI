"""
Chat management service - Pure DB layer + Single SaveManager
"""

import streamlit as st
import sqlite3
import uuid
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from config.settings import DATABASE_PATH, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, DEFAULT_MODEL
from utils.logger import setup_logging

logger = setup_logging()

SCHEMA_VERSION = 1
MAX_MESSAGE_SIZE = 1024 * 1024
MAX_CONVERSATION_LENGTH = 10000
SAVE_DELAY_SECONDS = 2.0
SAVE_COOLDOWN_SECONDS = 1.0

# ============================================================================
# PURE DATABASE LAYER (NO Streamlit state, NO cooldown logic)
# ============================================================================

def get_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def get_time_seconds() -> float:
    return time.time()

def get_display_time(iso_timestamp: str) -> str:
    try:
        clean_ts = iso_timestamp.replace('Z', '+00:00')
        dt = datetime.fromisoformat(clean_ts)
        return dt.strftime("%H:%M:%S")
    except:
        return ""

def init_database():
    Path("data").mkdir(exist_ok=True)
    
    for attempt in range(5):
        try:
            with sqlite3.connect(DATABASE_PATH, timeout=30) as conn:
                c = conn.cursor()
                c.execute("PRAGMA journal_mode=WAL")
                c.execute("PRAGMA synchronous=NORMAL")
                c.execute("PRAGMA busy_timeout=30000")
                
                c.execute('''CREATE TABLE IF NOT EXISTS chats
                             (id TEXT PRIMARY KEY,
                              name TEXT,
                              created_at TEXT,
                              updated_at TEXT,
                              raw_messages TEXT,
                              schema_version INTEGER DEFAULT 1,
                              message_count INTEGER DEFAULT 0)''')
                
                c.execute("CREATE INDEX IF NOT EXISTS idx_updated_at ON chats(updated_at DESC)")
                c.execute('''CREATE TABLE IF NOT EXISTS metadata
                             (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)''')
                
                c.execute('''INSERT OR REPLACE INTO metadata (key, value, updated_at)
                             VALUES (?, ?, ?)''', ('schema_version', str(SCHEMA_VERSION), get_timestamp()))
                conn.commit()
            
            logger.info("Database initialized")
            return
        except sqlite3.OperationalError as e:
            if attempt < 4:
                time.sleep(0.5 * (2 ** attempt))
            else:
                raise

def validate_message(msg: dict) -> Tuple[bool, str]:
    if not isinstance(msg, dict):
        return False, f"Not a dict"
    if not all(k in msg for k in ["role", "content", "timestamp"]):
        return False, f"Missing keys"
    if msg["role"] not in ["user", "assistant"]:
        return False, f"Invalid role: {msg['role']}"
    if not isinstance(msg["content"], str) or not msg["content"].strip():
        return False, f"Invalid content"
    if len(msg["content"].encode('utf-8')) > MAX_MESSAGE_SIZE:
        return False, f"Too large"
    try:
        datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00'))
    except:
        return False, f"Invalid timestamp"
    return True, ""

def serialize(messages: list) -> str:
    for i, msg in enumerate(messages):
        valid, err = validate_message(msg)
        if not valid:
            raise ValueError(f"Message {i}: {err}")
    return json.dumps({"version": SCHEMA_VERSION, "messages": messages}, separators=(',', ':'))

def deserialize(data: str) -> Tuple[list, bool, str]:
    try:
        parsed = json.loads(data)
        if isinstance(parsed, dict) and "messages" in parsed:
            msgs = parsed["messages"]
            original_len = len(msgs)
            valid_msgs = [m for m in msgs if validate_message(m)[0]]
            if len(valid_msgs) != original_len:
                return valid_msgs, True, f"Recovered {len(valid_msgs)}/{original_len}"
            return valid_msgs, False, ""
        elif isinstance(parsed, list):
            return parsed, False, "Legacy format"
        return [], True, "Invalid format"
    except:
        return [], True, "JSON error"

def db_save_chat(chat_id: str, name: str, messages: list) -> bool:
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=30) as conn:
            conn.execute("BEGIN IMMEDIATE")
            c = conn.cursor()
            c.execute("SELECT id FROM chats WHERE id = ?", (chat_id,))
            exists = c.fetchone()
            if exists:
                c.execute('''UPDATE chats SET name=?, updated_at=?, raw_messages=?, message_count=?
                             WHERE id=?''',
                          (name, get_timestamp(), serialize(messages), len(messages), chat_id))
            else:
                c.execute('''INSERT INTO chats (id, name, created_at, updated_at, raw_messages, schema_version, message_count)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (chat_id, name, get_timestamp(), get_timestamp(), serialize(messages), SCHEMA_VERSION, len(messages)))
            conn.commit()
        return True
    except Exception as e:
        logger.exception(f"DB save failed: {e}")
        return False

def db_load_chats() -> dict:
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=30) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, raw_messages, created_at, updated_at FROM chats ORDER BY updated_at DESC")
            rows = c.fetchall()
        
        chats = {}
        for row in rows:
            chat_id, name, raw_json, created_at, updated_at = row
            messages, corrupted, msg = deserialize(raw_json)
            if messages:
                chats[chat_id] = {
                    "name": name,
                    "messages": messages,
                    "created_at": created_at,
                    "updated_at": updated_at
                }
                if corrupted:
                    logger.warning(f"Chat {chat_id}: {msg}")
        return chats
    except Exception as e:
        logger.error(f"Load failed: {e}")
        return {}

def db_delete_chat(chat_id: str):
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=30) as conn:
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"Delete failed: {e}")

# ============================================================================
# SAVEMANAGER: Single source of truth for ALL save decisions
# ============================================================================

class SaveManager:
    """Manages ALL save decisions - single entry point for persistence"""
    
    def __init__(self):
        self._init()
    
    def _init(self):
        if '_save_request_time' not in st.session_state:
            st.session_state._save_request_time = 0
        if '_save_request_chat_id' not in st.session_state:
            st.session_state._save_request_chat_id = None
        if '_save_pending' not in st.session_state:
            st.session_state._save_pending = False
        if '_last_save_time' not in st.session_state:
            st.session_state._last_save_time = 0
        if '_last_save_chat_id' not in st.session_state:
            st.session_state._last_save_chat_id = None
    
    def request_save(self, chat_id: str, reason: str = "unknown"):
        now = get_time_seconds()
        st.session_state._save_request_time = now
        st.session_state._save_request_chat_id = chat_id
        st.session_state._save_pending = True
        logger.debug(f"Save requested: {reason} for chat {chat_id[:8]}")
    
    def force_save_now(self, chat_id: str) -> bool:
        if st.session_state._save_pending and st.session_state._save_request_chat_id == chat_id:
            return self._execute_save(chat_id)
        return False
    
    def should_save(self) -> Tuple[bool, Optional[str]]:
        if not st.session_state._save_pending:
            return False, None
        
        last_time = st.session_state._last_save_time
        last_id = st.session_state._last_save_chat_id
        current_id = st.session_state._save_request_chat_id
        now = get_time_seconds()
        
        if last_id == current_id and (now - last_time) < SAVE_COOLDOWN_SECONDS:
            logger.debug(f"Save skipped (cooldown): {current_id[:8]}")
            return False, None
        
        request_time = st.session_state._save_request_time
        if (now - request_time) >= SAVE_DELAY_SECONDS:
            return True, st.session_state._save_request_chat_id
        
        return False, None
    
    def _execute_save(self, chat_id: str) -> bool:
        if chat_id != st.session_state.get('current_chat_id'):
            logger.warning(f"Cannot save {chat_id[:8]}: not current chat")
            return False
        
        chat = st.session_state.chats.get(chat_id)
        if not chat:
            logger.warning(f"Cannot save {chat_id[:8]}: chat not found")
            return False
        
        success = db_save_chat(chat_id, chat["name"], st.session_state.current_messages)
        
        if success:
            st.session_state._last_save_time = get_time_seconds()
            st.session_state._last_save_chat_id = chat_id
            logger.debug(f"Saved chat {chat_id[:8]} ({len(st.session_state.current_messages)} messages)")
        else:
            logger.error(f"Save failed for chat {chat_id[:8]}")
        
        st.session_state._save_pending = False
        st.session_state._save_request_chat_id = None
        
        return success
    
    def tick(self) -> bool:
        should_save, chat_id = self.should_save()
        if should_save and chat_id:
            return self._execute_save(chat_id)
        return False

_save_manager = None

def get_save_manager() -> SaveManager:
    global _save_manager
    if _save_manager is None:
        _save_manager = SaveManager()
    return _save_manager

# ============================================================================
# BUSINESS LOGIC
# ============================================================================

def init():
    init_database()
    
    if 'chats' not in st.session_state:
        st.session_state.chats = db_load_chats()
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None
    if 'current_messages' not in st.session_state:
        if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
            st.session_state.current_messages = st.session_state.chats[st.session_state.current_chat_id]["messages"].copy()
        else:
            st.session_state.current_messages = []
    if 'temperature' not in st.session_state:
        st.session_state.temperature = DEFAULT_TEMPERATURE
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = DEFAULT_MAX_TOKENS
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = DEFAULT_MODEL
    if 'show_settings' not in st.session_state:
        st.session_state.show_settings = False
    if 'export_format' not in st.session_state:
        st.session_state.export_format = "Markdown"
    
    get_save_manager()

def check_and_save():
    return get_save_manager().tick()

def new_chat():
    manager = get_save_manager()
    if st.session_state.current_chat_id:
        manager.force_save_now(st.session_state.current_chat_id)
    
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = chat_id
    st.session_state.current_messages = []
    st.session_state.chats[chat_id] = {
        "name": "New Chat",
        "messages": [],
        "created_at": get_timestamp(),
        "updated_at": get_timestamp()
    }
    st.rerun()

def switch_chat(chat_id: str):
    manager = get_save_manager()
    if st.session_state.current_chat_id:
        manager.force_save_now(st.session_state.current_chat_id)
    
    if chat_id in st.session_state.chats:
        st.session_state.current_chat_id = chat_id
        st.session_state.current_messages = st.session_state.chats[chat_id]["messages"].copy()
        st.rerun()

def delete_chat_by_id(chat_id: str):
    manager = get_save_manager()
    if chat_id == st.session_state.current_chat_id:
        manager.force_save_now(chat_id)
    
    if chat_id in st.session_state.chats:
        db_delete_chat(chat_id)
        del st.session_state.chats[chat_id]
        if st.session_state.current_chat_id == chat_id:
            st.session_state.current_chat_id = None
            st.session_state.current_messages = []
        st.rerun()

def add_user_message(content: str) -> bool:
    if not st.session_state.current_chat_id:
        new_chat()
    
    msg = {
        "role": "user",
        "content": content,
        "timestamp": get_timestamp()
    }
    
    valid, err = validate_message(msg)
    if not valid:
        st.error(f"Invalid message: {err}")
        return False
    
    st.session_state.current_messages.append(msg)
    st.session_state.chats[st.session_state.current_chat_id]["messages"] = st.session_state.current_messages.copy()
    st.session_state.chats[st.session_state.current_chat_id]["updated_at"] = get_timestamp()
    
    chat = st.session_state.chats[st.session_state.current_chat_id]
    if chat["name"] == "New Chat":
        chat["name"] = _generate_name(content)
    
    get_save_manager().request_save(st.session_state.current_chat_id, "user_message")
    return True

def add_assistant_message(content: str) -> bool:
    msg = {
        "role": "assistant",
        "content": content,
        "timestamp": get_timestamp()
    }
    
    valid, err = validate_message(msg)
    if not valid:
        st.error(f"Invalid response: {err}")
        return False
    
    st.session_state.current_messages.append(msg)
    st.session_state.chats[st.session_state.current_chat_id]["messages"] = st.session_state.current_messages.copy()
    st.session_state.chats[st.session_state.current_chat_id]["updated_at"] = get_timestamp()
    
    get_save_manager().request_save(st.session_state.current_chat_id, "assistant_message")
    return True

def remove_last_message():
    if st.session_state.current_messages:
        st.session_state.current_messages.pop()
        if st.session_state.current_chat_id:
            st.session_state.chats[st.session_state.current_chat_id]["messages"] = st.session_state.current_messages.copy()

def _generate_name(first_message: str) -> str:
    if not first_message:
        return "New Chat"
    name = first_message.strip()[:40]
    prefixes = ["how to ", "what is ", "why is ", "can you ", "please ", "tell me "]
    for p in prefixes:
        if name.lower().startswith(p):
            name = name[len(p):]
            break
    if name:
        name = name[0].upper() + name[1:]
    else:
        name = "New Chat"
    return name

def get_messages():
    return st.session_state.current_messages

def get_all_chats():
    return st.session_state.chats

def get_current_id():
    return st.session_state.current_chat_id

def get_settings():
    return {
        "temperature": st.session_state.temperature,
        "max_tokens": st.session_state.max_tokens,
        "model": st.session_state.selected_model,
        "export_format": st.session_state.export_format,
        "show_settings": st.session_state.show_settings
    }

def set_show_settings(value: bool):
    st.session_state.show_settings = value

def set_export_format(value: str):
    st.session_state.export_format = value

def set_temperature(value: float):
    st.session_state.temperature = value

def set_max_tokens(value: int):
    st.session_state.max_tokens = value

def set_model(value: str):
    st.session_state.selected_model = value

# ============================================================================
# COMPUTED VIEWS
# ============================================================================

def filter_for_gemini(messages: list) -> list:
    result = []
    for msg in messages:
        valid, _ = validate_message(msg)
        if valid:
            role = "model" if msg["role"] == "assistant" else "user"
            result.append({"role": role, "parts": [msg["content"]]})
    return result

def get_display_list(messages: list) -> list:
    return [{"role": m["role"], "content": m["content"], "display_time": get_display_time(m["timestamp"])} for m in messages]