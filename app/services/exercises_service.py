import re

from app.config import WORDS_FILE
from app.storage import read_json, write_json
from app.database import db
from app.models import Chapter

# Ex.: chapter-01 (só minúsculas, números e hífen)
LESSON_ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def get_chapter_data(chapter):
    """Devolve a linha do capítulo.

    Levanta LookupError se o id for inválido ou a linha não existir.
    """
    if not LESSON_ID_PATTERN.match(chapter):
        raise LookupError("Capítulo não encontrado.")

    row = db.session.get(Chapter, chapter)

    if row is None:
        raise LookupError("Capítulo não encontrado.")

    return row


def get_pronunciation(lesson_id):
    """Devolve os dados de pronúncia de um capítulo.

    Levanta LookupError se o id for inválido ou o capítulo não existir.
    """
    return get_chapter_data(lesson_id).to_dict()


def create_word(word):
    """Cadastra uma palavra. Levanta ValueError se for inválida."""
    if not isinstance(word, str) or not word.strip():
        raise ValueError("Digite uma palavra válida.")

    words = read_json(WORDS_FILE)

    new_word = {
        "id": max((item["id"] for item in words), default=0) + 1,
        "word": word.strip(),
    }

    words.append(new_word)
    write_json(WORDS_FILE, words)

    return new_word