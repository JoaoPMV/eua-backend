from app.routes.audio import audio_bp
from app.routes.words import words_bp


def register_routes(app):
    app.register_blueprint(words_bp)
    app.register_blueprint(audio_bp)