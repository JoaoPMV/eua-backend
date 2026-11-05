from flask import Blueprint, send_from_directory

from app.config import AUDIO_DIR

audio_bp = Blueprint("audio", __name__)


@audio_bp.get("/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)