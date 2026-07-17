"""Entry point — composition root da API da Loja (MVC)."""

from src.app import app, create_app
from src.config.settings import settings

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
