from functools import lru_cache

from pydantic import Field, model_validator
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
    audit_log_signing_key: str = Field(
        default="replace-with-production-audit-signing-key",
        validation_alias="AUDIT_LOG_SIGNING_KEY",
    )
    api_key: str = Field(default="dev-local-api-key", validation_alias="API_KEY")
    api_key_scopes: str = Field(
        default="analysis:read,analysis:write,agent:ask,privacy:admin",
        validation_alias="API_KEY_SCOPES",
    )
    rate_limit_requests_per_minute: int = 60
    require_user_consent: bool = True
    default_retention_days: int = 30
    raw_artifact_retention_hours: int = 0
    action_log_path: str = "logs/actions.log"
    action_log_max_bytes: int = 5_000_000
    security_headers_enabled: bool = True
    allowed_hosts: str = Field(default="*", validation_alias="ALLOWED_HOSTS")
    cors_allowed_origins: str = Field(default="", validation_alias="CORS_ALLOWED_ORIGINS")
    threat_feed_refresh_seconds: int = 3600
    enable_external_ai: bool = False
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.environment.lower() == "production":
            unsafe_values = {
                "API_KEY": self.api_key == "dev-local-api-key",
                "ENCRYPTION_KEY": self.encryption_key == "replace-with-32-byte-production-key",
                "AUDIT_LOG_SIGNING_KEY": self.audit_log_signing_key
                == "replace-with-production-audit-signing-key",
            }
            unsafe = [name for name, is_unsafe in unsafe_values.items() if is_unsafe]
            if unsafe:
                raise ValueError(f"Unsafe production configuration for: {', '.join(unsafe)}")
            if self.raw_artifact_retention_hours != 0:
                raise ValueError("Production raw artifact retention must remain 0 by default.")
        return self

    @property
    def allowed_host_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
