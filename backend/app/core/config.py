import os
from pathlib import Path
from dotenv import load_dotenv

# backend/app/core/config.py
# parent = core
# parent.parent = app
# parent.parent.parent = backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROMPT_DIR = BASE_DIR / "app" / "prompts"

if not OPENAI_API_KEY:
    raise RuntimeError("没有读取到 OPENAI_API_KEY，请检查 backend/.env")
