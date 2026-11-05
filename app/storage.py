import json
from pathlib import Path

from app.config import DATA_DIR, WORDS_FILE


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def init_storage():
    """Cria a pasta de dados e o words.json se ainda não existirem."""
    DATA_DIR.mkdir(exist_ok=True)

    if not WORDS_FILE.exists():
        write_json(WORDS_FILE, [])