"""
Application configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# App settings
APP_NAME = "SakibAI"
APP_VERSION = "4.0"

# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model defaults
DEFAULT_MODEL = "Gemini"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000
DEFAULT_MODEL_NAME = "gemini-2.0-flash-exp"

# Available models
AVAILABLE_MODELS = ["Gemini"]

# Export formats
EXPORT_FORMATS = ["Markdown", "TXT"]

# Database
DATABASE_PATH = "data/chats.db"