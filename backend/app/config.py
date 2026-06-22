import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-troque-em-producao")

    # SQLAlchemy / PostgreSQL
    # Alguns provedores (Heroku, Railway) entregam a URL como "postgres://",
    # esquema que o SQLAlchemy 2.x não aceita — normaliza para "postgresql://".
    _database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/keepr",
    )
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]

    # APScheduler
    SCHEDULER_API_ENABLED = False
    SCHEDULER_TIMEZONE = "America/Sao_Paulo"

    # Uploads
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "uploads"
    )
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

    # OCR — Gemini Vision
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    # Resend — email transacional
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "Keepr <onboarding@resend.dev>")
    EMAIL_TO_OVERRIDE = os.getenv("EMAIL_TO_OVERRIDE", "")

    # CORS — separadas por vírgula
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:4173",
    ).split(",")


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/keepr_test",
    )
