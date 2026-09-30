import os
from pathlib import Path

import certifi
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

for _dir in (DATA_DIR, UPLOADS_DIR, CHROMA_DIR):
    _dir.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{(DATA_DIR / 'chatbot_memory.db').as_posix()}"
CHECKPOINT_DB_PATH = str(DATA_DIR / "langgraph_checkpoints.sqlite")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-120b")

# model name -> provider ("google", "groq")
# API keys come from .env: GOOGLE_API_KEY, GROQ_API_KEY
MODEL_PROVIDERS = {
    "gemini-3.1-flash-lite": "google",
    "gemini-3.5-flash": "google",
    "gemini-3.1-pro-preview": "google",
    "gemini-2.5-pro": "google",
    "openai/gpt-oss-120b": "groq",
    "openai/gpt-oss-20b": "groq",
    "qwen/qwen3.8-27b": "groq",
}

ALLOWED_MODELS = set(MODEL_PROVIDERS)

EMBEDDING_MODEL = "gemini-embedding-001"
CHROMA_COLLECTION = "agentic_chatbot_docs"

ALLOWED_UPLOAD_EXTENSIONS = [".pdf", ".docx", ".txt", ".md", ".py", ".csv"]
