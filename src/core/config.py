"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "PUAR-Patients"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "puar"
    db_password: str = "puar_secret"
    db_name: str = "puar_patients"

    @computed_field
    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
                path=self.db_name,
            )
        )

    @computed_field
    @property
    def database_url_sync(self) -> str:
        """Construct sync PostgreSQL connection URL for Alembic."""
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
                path=self.db_name,
            )
        )

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AWS (for notifications)
    aws_region: str = "eu-west-1"
    aws_ses_sender_email: str = ""
    aws_sns_enabled: bool = False

    # Feature flags
    sms_notifications_enabled: bool = False
    email_notifications_enabled: bool = True
    demo_mode_enabled: bool = True  # Enable demo login endpoint


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
