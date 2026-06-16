from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Mobile Privacy Guardian Agent"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    environment: str = Field(default="local", validation_alias="ENVIRONMENT")
    database_url: str = "sqlite+aiosqlite:///./privacy_guardian.db"
    redis_url: str = "redis://localhost:6379/0"
    encryption_key: str = "replace-with-32-byte-production-key"
    api_key: str = Field(default="dev-local-api-key", validation_alias="API_KEY")
    api_key_scopes: str = Field(
        default="analysis:read,analysis:write,agent:ask,privacy:admin",
        validation_alias="API_KEY_SCOPES",
    )
    rate_limit_requests_per_minute: int = 60
    require_user_consent: bool = True
    default_retention_days: int = 30
    raw_artifact_retention_hours: int = 0
    threat_feed_refresh_seconds: int = 3600
    enable_external_ai: bool = False
    openai_api_key: str | None = None
    gemini_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
