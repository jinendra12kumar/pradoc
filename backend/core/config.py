from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:12345@localhost:5432/pradoc_db"
    DATABASE_TYPE: str = "postgresql"

    # ── JWT ───────────────────────────────────────────────
    SECRET_KEY: str = "changeme-set-in-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── RabbitMQ / Celery ─────────────────────────────────
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # ── Gmail SMTP ────────────────────────────────────────
    GMAIL: str = ""
    APPPASSWORD: str = ""
    EMAIL_FROM_NAME: str = "PraDoc Health"

    # ── OTP ───────────────────────────────────────────────
    OTP_EXPIRE_SECONDS: int = 300
    OTP_MAX_ATTEMPTS: int = 3

    # ── File Uploads ──────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"

    # ── App ───────────────────────────────────────────────
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
