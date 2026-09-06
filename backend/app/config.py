"""Application configuration loaded via Pydantic settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Centralized application settings with strict validation."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Not Your Therapist API"
    APP_VERSION: str = "0.2.0"
    APP_DESCRIPTION: str = "Not a real Therapist chatbot using Ollama, and Langchain"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = Field(..., description="Database connection string")
    OLLAMA_BASE_URL: str = Field(..., description="Ollama server URL")
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]

    @field_validator("DATABASE_URL", "OLLAMA_BASE_URL")
    @classmethod
    def validate_required_env(cls, value: str | None) -> str:
        """Reject empty or missing environment values."""
        if value is None or not value.strip():
            raise ValueError("must be set")
        return value.strip()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
