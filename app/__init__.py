from flask import Flask
from flask_cors import CORS

from app.routes import register_routes
from app.storage import init_storage
from app.config import SQLALCHEMY_DATABASE_URI
from app.database import db


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    db.init_app(app)
    CORS(app)

    init_storage()
    register_routes(app)

    return app