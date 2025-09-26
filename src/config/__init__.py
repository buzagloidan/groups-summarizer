from os import environ
from typing import Optional, Self

from pydantic import model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API settings - Railway uses PORT environment variable
    port: int = Field(default=8000, env="PORT")
    host: str = "0.0.0.0"

    # Database settings
    db_uri: str

    # WhatsApp settings
    whatsapp_host: str
    whatsapp_basic_auth_password: Optional[str] = None
    whatsapp_basic_auth_user: Optional[str] = None

    anthropic_api_key: str

    # Monitor settings for daily summaries
    monitor_phone: Optional[str] = None
    secret_word: Optional[str] = None

    # Optional settings
    debug: bool = False
    log_level: str = "INFO"
    logfire_token: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        arbitrary_types_allowed=True,
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def async_db_uri(self) -> str:
        """Convert DB URI to use asyncpg driver"""
        if self.db_uri.startswith("postgresql://"):
            return self.db_uri.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.db_uri

    @model_validator(mode="after")
    def apply_env(self) -> Self:
        if self.anthropic_api_key:
            environ["ANTHROPIC_API_KEY"] = self.anthropic_api_key

        if self.logfire_token:
            environ["LOGFIRE_TOKEN"] = self.logfire_token

        return self
