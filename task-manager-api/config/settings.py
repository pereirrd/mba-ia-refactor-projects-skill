import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    NOTIFICATIONS_ENABLED = (
        os.environ.get("NOTIFICATIONS_ENABLED", "false").lower() == "true"
    )
    APP_VERSION = "2.0.0"
    VALID_STATUSES = ("pending", "in_progress", "done", "cancelled")
    VALID_ROLES = ("user", "admin", "manager")
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_PASSWORD_LENGTH = 4
    DEFAULT_PRIORITY = 3
    DEFAULT_COLOR = "#000000"


settings = Settings()
