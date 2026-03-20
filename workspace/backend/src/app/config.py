"""
Application configuration via Pydantic Settings.
All values are loaded from environment variables (or .env files).
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Central settings object — injected from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=True,
        # Silently ignore extra env vars that aren't declared here
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # App
    # ------------------------------------------------------------------
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    API_TITLE: str = "Fashion Tech API"
    API_VERSION: str = "0.1.0"
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"  # generic app secret

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = (
        "postgresql+asyncpg://developer:dev_password_123@localhost:5432/fashion_tech_dev"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # ------------------------------------------------------------------
    # JWT / Auth
    # ------------------------------------------------------------------
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------
    # AWS / S3 (MinIO-compatible)
    # ------------------------------------------------------------------
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_ENDPOINT_URL: Optional[str] = None  # None → use AWS; set for MinIO
    S3_BUCKET: str = "fashion-tech-storage"
    S3_PRESIGNED_URL_EXPIRY: int = 3600  # seconds

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" | "text"

    # ------------------------------------------------------------------
    # Feature flags
    # ------------------------------------------------------------------
    ENABLE_DOCS: bool = True  # Disable in production if desired
    ENABLE_METRICS: bool = False

    # ------------------------------------------------------------------
    # Computed helpers
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT == Environment.TEST

    @property
    def docs_url(self) -> Optional[str]:
        return "/docs" if self.ENABLE_DOCS else None

    @property
    def redoc_url(self) -> Optional[str]:
        return "/redoc" if self.ENABLE_DOCS else None


# Singleton — import this throughout the app
settings = Settings()
