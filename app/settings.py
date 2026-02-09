# app/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

class Settings:

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()
