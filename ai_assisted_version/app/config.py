from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = ""
    redis_url: str = "redis://localhost:6379/1"
    secret_key: str = ""
    internal_billing_key: str = ""
    algorithm: str = "HS256"
    access_token_minutes: int = 30
    max_body_bytes: int = 65536
    admin_password: str = "AdminPass123!"
    demo_password: str = "ClientPass123!"

    @field_validator("database_url", "secret_key", "internal_billing_key")
    @classmethod
    def validate_required_secret(cls, value: str, info) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError(f"{info.field_name} is required")
        blocked_markers = ("change-me", "changeme", "replace_with", "example", "demo_secret")
        if any(marker in normalized for marker in blocked_markers):
            raise ValueError(f"{info.field_name} must be changed from example value")
        if info.field_name == "secret_key" and len(value) < 32:
            raise ValueError("secret_key must be at least 32 characters")
        if info.field_name == "internal_billing_key" and len(value) < 24:
            raise ValueError("internal_billing_key must be at least 24 characters")
        return value


settings = Settings()
