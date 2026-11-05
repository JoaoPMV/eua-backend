import json

from flask import Blueprint, jsonify, request

from app.services import exercises_service

words_bp = Blueprint("words", __name__)

@words_bp.get("/pronunciation/<lesson_id>")
def get_pronunciation(lesson_id):
    try:
        lesson = exercises_service.get_pronunciation(lesson_id)
    except LookupError as error:
        return jsonify({"error": str(error)}), 404
    except json.JSONDecodeError:
        return jsonify({
            "error": "O arquivo de pronúncia do capítulo contém JSON inválido."
        }), 500

    return jsonify(lesson), 200


@words_bp.post("/words")
def create_word():
    data = request.get_json(silent=True) or {}

    try:
        new_word = exercises_service.create_word(data.get("word", ""))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({
        "message": "Palavra cadastrada com sucesso!",
        "word": new_word,
    }), 201