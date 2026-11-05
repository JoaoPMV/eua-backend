import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

# backend/
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = BASE_DIR / "audio"

WORDS_FILE = DATA_DIR / "vocabulary.json"
WORD_AUDIO_DIR = DATA_DIR / "word-audio"