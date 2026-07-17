import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.middlewares.error_handler import register_error_handlers
from src.models.database import get_connection
from src.views.routes import register_routes

logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    if settings.CORS_ORIGINS == "*":
        CORS(app)
    else:
        CORS(app, resources={r"/*": {"origins": settings.CORS_ORIGINS.split(",")}})

    register_error_handlers(app)
    register_routes(app)
    get_connection()
    return app


app = create_app()


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
