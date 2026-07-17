import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    APP_VERSION = "2.0.0"

    CATEGORIAS_VALIDAS = (
        "informatica",
        "moveis",
        "vestuario",
        "geral",
        "eletronicos",
        "livros",
    )
    STATUS_PEDIDO_VALIDOS = (
        "pendente",
        "aprovado",
        "enviado",
        "entregue",
        "cancelado",
    )
    DESCONTO_FAIXAS = (
        (10000, 0.10),
        (5000, 0.05),
        (1000, 0.02),
    )


settings = Settings()
