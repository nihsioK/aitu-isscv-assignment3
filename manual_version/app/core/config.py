from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = ""
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = ""
    internal_api_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    max_request_size_bytes: int = 65536
    admin_initial_password: str = "AdminPass123!"
    demo_client_password: str = "ClientPass123!"

    debug: bool = False

    @field_validator("database_url", "secret_key", "internal_api_key")
    @classmethod
    def validate_required_secret(cls, value: str, info) -> str:
        if not value.strip():
            raise ValueError(f"{info.field_name} is required")
        lowered = value.lower()
        if "change-me" in lowered or "changeme" in lowered:
            raise ValueError(f"{info.field_name} must be changed from example value")
        if info.field_name == "secret_key" and len(value) < 32:
            raise ValueError(f"{info.field_name} must be at least 32 characters")
        if info.field_name == "internal_api_key" and len(value) < 24:
            raise ValueError(f"{info.field_name} must be at least 24 characters")
        return value


settings = Settings()
